"""Run a problem's tests and return a structured report.

code    → unit tests: compile your files + forge_test.c + tests with sanitizers, run, parse JSON lines
          e2e: build your compiler, compile each case's mini-C source, assemble, run, compare exit/stdout
quiz    → compare chosen option (1-based) to `answer` (0-based index in problem.toml)
predict → compare typed text to `answer` (or any of `answers`), whitespace-normalized
"""

from __future__ import annotations

import json
import re
import os
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from .course import Course, Problem

CFLAGS = [
    "-std=c11", "-g", "-O0", "-Wall", "-Wextra",
    "-fsanitize=address,undefined", "-fno-sanitize-recover=undefined", "-fno-omit-frame-pointer",
]


@dataclass
class TestResult:
    name: str
    status: str  # pass | fail | crash | timeout
    hidden: bool = False
    line: int | None = None
    file: str | None = None
    expr: str | None = None
    expected: str | None = None
    got: str | None = None
    output: str = ""
    signal: str | None = None
    source: list[tuple[int, str]] | None = None  # (line no, text) of a failing visible test's body
    mark: int | None = None  # line no in that body where it failed or crashed


@dataclass
class Report:
    kind: str
    hidden: bool  # whether hidden tests were included (submit)
    compiled: bool = True
    compile_output: str = ""
    results: list[TestResult] = field(default_factory=list)
    message: str = ""  # quiz feedback
    correct: bool | None = None  # quiz result

    @property
    def passed(self) -> bool:
        if self.kind != "code":
            return bool(self.correct)
        return self.compiled and bool(self.results) and all(r.status == "pass" for r in self.results)

    @property
    def summary(self) -> str:
        if self.kind != "code":
            return "correct" if self.correct else "not quite"
        if not self.compiled:
            return "compile error"
        n = sum(r.status == "pass" for r in self.results)
        return f"{n}/{len(self.results)} tests passed"


def run_code(course: Course, problem: Problem, src_dir: Path, hidden: bool) -> Report:
    report = Report("code", hidden)
    build = Path(tempfile.mkdtemp(prefix="forge-build-"))
    flags = CFLAGS + (["-Werror"] if problem.werror else [])
    try:
        if problem.has_unit_tests and not _unit_tests(report, course, problem, src_dir, hidden, build, flags):
            return report
        if problem.e2e:
            _e2e_tests(report, problem, src_dir, hidden, build, flags)
        _attach_sources(report, problem.test_files(False))
        return report
    finally:
        shutil.rmtree(build, ignore_errors=True)


def _c_sources(problem: Problem, src_dir: Path, with_main: bool) -> tuple[list[str], list[str]]:
    """(sources, include flags). A project builds src/*.c; unit tests leave out src/main.c."""
    if problem.mode == "project":
        root = src_dir / "src"
        srcs = [p for p in sorted(root.glob("*.c")) if with_main or p.name != "main.c"]
        return [str(p) for p in srcs], [f"-I{root}"]
    return [str(p) for p in sorted(src_dir.glob("*.c"))], [f"-I{src_dir}"]


def _unit_tests(report: Report, course: Course, problem: Problem, src_dir: Path, hidden: bool,
                build: Path, flags: list[str]) -> bool:
    exe = build / "tests"
    sources, incs = _c_sources(problem, src_dir, with_main=False)
    tests = [str(t) for t in problem.test_files(hidden)]
    cmd = ["cc", *flags, *incs, f"-I{course.harness_dir}",
           *sources, str(course.harness_dir / "forge_test.c"), *tests, "-o", str(exe)]
    proc = subprocess.run(cmd, capture_output=True, text=True, errors="backslashreplace", cwd=src_dir,
                          stdin=subprocess.DEVNULL)
    report.compile_output = _clean(proc.stderr, src_dir, course)
    if proc.returncode != 0:
        report.compiled = False
        return False
    env = {**os.environ,
           "FORGE_TIMEOUT": str(problem.data.get("timeout_s", 2)),
           "ASAN_OPTIONS": "detect_leaks=0:abort_on_error=0",
           "UBSAN_OPTIONS": "print_stacktrace=1"}
    try:
        # A buggy string (no '\0') makes the harness print raw memory: keep invalid bytes, show them as \xNN.
        run = subprocess.run([str(exe)], capture_output=True, text=True, errors="surrogateescape", timeout=60,
                             env=env, cwd=src_dir, stdin=subprocess.DEVNULL)
    except subprocess.TimeoutExpired:
        report.results.append(TestResult("(harness)", "timeout"))
        return True
    for line in run.stdout.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            raw = {k: _bytes_visible(v) if isinstance(v, str) else v for k, v in json.loads(line).items()}
        except json.JSONDecodeError:
            continue
        raw["output"] = _clean(raw.get("output", ""), src_dir, course)
        report.results.append(TestResult(**{k: raw.get(k) for k in TestResult.__dataclass_fields__ if k in raw}))
    return True


def _numbered(text: str, limit: int = 30) -> str:
    lines = text.rstrip("\n").split("\n")
    out = [f"{i:>3}  {ln}" for i, ln in enumerate(lines[:limit], 1)]
    if len(lines) > limit:
        out.append(f"     … ({len(lines) - limit} more lines)")
    return "\n".join(out)


def _proc(cmd: list[str], timeout: float, stdin: str = "") -> subprocess.CompletedProcess:
    return subprocess.run(cmd, input=stdin, capture_output=True, text=True, errors="backslashreplace",
                          timeout=timeout, env={**os.environ, "ASAN_OPTIONS": "detect_leaks=0"})


def _e2e_tests(report: Report, problem: Problem, src_dir: Path, hidden: bool, build: Path,
               flags: list[str]) -> None:
    """For each case: your compiler turns `source` into assembly, `cc` assembles it, the program runs.
    With e2e_program = "asm" the program is your own .s file instead (chapter 1 warm-up)."""
    timeout = float(problem.data.get("timeout_s", 2))
    asm_mode = problem.data.get("e2e_program") == "asm"
    mcc = build / "mcc"
    if not asm_mode:
        sources, incs = _c_sources(problem, src_dir, with_main=True)
        proc = subprocess.run(["cc", *flags, *incs, *sources, "-o", str(mcc)], capture_output=True, text=True,
                              errors="backslashreplace", cwd=src_dir, stdin=subprocess.DEVNULL)
        out = _clean(proc.stderr, src_dir, problem.course)
        if out and out not in report.compile_output:
            report.compile_output += out
        if proc.returncode != 0:
            report.compiled = False
            return
    for i, case in enumerate(c for c in problem.e2e if hidden or not c.get("hidden")):
        r = TestResult(case["name"], "pass", hidden=bool(case.get("hidden")))
        source = case.get("source", "")
        if source and not r.hidden:
            r.source = [(n, ln) for n, ln in enumerate(source.rstrip("\n").split("\n"), 1)]
        try:
            _e2e_case(r, case, i, asm_mode, mcc, src_dir, problem, build, timeout)
        except subprocess.TimeoutExpired as e:
            r.status = "timeout"
            r.output = f"timed out running {Path(e.cmd[0]).name}"
        if r.hidden:
            r.output = ""  # a hidden case shows its name and the mismatch only
        report.results.append(r)


def _e2e_case(r: TestResult, case: dict, i: int, asm_mode: bool, mcc: Path, src_dir: Path,
              problem: Problem, build: Path, timeout: float) -> None:
    def fail(expr: str, expected, got, output: str = "") -> None:
        r.status, r.expr, r.expected, r.got, r.output = "fail", expr, str(expected), str(got), output

    if asm_mode:
        asm_path = src_dir / problem.edit_files[0]
    else:
        src = build / f"t{i}.c"
        src.write_text(case.get("source", ""))
        asm_path = build / f"t{i}.s"
        cp = _proc([str(mcc), str(src), "-o", str(asm_path)], timeout)
        err = cp.stderr.replace(str(build) + "/", "")
        if "Sanitizer" in err or cp.returncode < 0:
            r.status, r.output = "crash", "your compiler crashed:\n" + err
            return
        if case.get("expect_compile_error"):
            if cp.returncode == 0:
                fail("mcc exit status", "non-zero (reject the program)", 0,
                     "accepted, and produced:\n" + _numbered(asm_path.read_text() if asm_path.exists() else ""))
            else:
                r.output = err.strip()  # show the error message it printed
            return
        if cp.returncode != 0:
            fail("mcc exit status", 0, cp.returncode, err)
            return
    asm = asm_path.read_text() if asm_path.exists() else ""
    listing = "your assembly:\n" + _numbered(asm)
    for word in case.get("asm_contains", []):
        if not re.search(rf"\b{re.escape(word)}\b", re.sub(r"//.*", "", asm)):
            fail("assembly uses", repr(word), "not found", listing)
            return
    exe = build / f"t{i}"
    ap = _proc(["cc", str(asm_path), "-o", str(exe)], timeout)
    if ap.returncode != 0:
        fail("build with cc (assemble + link)", "ok", "error",
             ap.stderr.replace(str(asm_path), asm_path.name).strip() + "\n" + listing)
        return
    pr = _proc([str(exe)], timeout, case.get("stdin", ""))
    if pr.returncode < 0:
        import signal
        r.status, r.signal, r.output = "crash", signal.Signals(-pr.returncode).name, listing
        return
    if "exit_code" in case and pr.returncode != case["exit_code"] % 256:
        fail("exit code", case["exit_code"] % 256, pr.returncode, listing)
        return
    if "stdout" in case and pr.stdout != case["stdout"]:
        fail("stdout", repr(case["stdout"]), repr(pr.stdout), listing)
        return


def _bytes_visible(s: str) -> str:
    """Turn undecodable bytes (surrogate-escaped) into a visible \\xNN."""
    return s.encode("utf-8", "surrogateescape").decode("utf-8", "backslashreplace")


def _attach_sources(report: Report, visible: list[Path]) -> None:
    """Give each failing visible test its source, so the learner sees what was exercised."""
    texts = {f.name: f.read_text().splitlines() for f in visible if f.exists()}
    for r in report.results:
        if r.status == "pass" or r.hidden or r.source:
            continue
        for fname, lines in texts.items():
            start = next((i for i, ln in enumerate(lines) if re.match(rf"\s*TEST\(\s*{re.escape(r.name)}\s*\)", ln)), None)
            if start is None:
                continue
            depth, end = 0, start
            for end in range(start, len(lines)):
                depth += lines[end].count("{") - lines[end].count("}")
                if depth <= 0 and "{" in "".join(lines[start:end + 1]):
                    break
            r.source = [(i + 1, lines[i]) for i in range(start + 1, end)]
            if r.status == "fail" and r.line:
                r.mark = r.line
            elif m := re.search(rf"{re.escape(fname)}:(\d+)", r.output):
                r.mark = int(m.group(1))
            break


def _clean(text: str, src_dir: Path, course: Course) -> str:
    """Shorten absolute paths so compiler/sanitizer output is readable."""
    text = text.replace(str(src_dir) + "/", "").replace(str(src_dir.resolve()) + "/", "")
    text = text.replace(str(course.dir) + "/", "")
    return text


def _norm(s: str) -> str:
    return " ".join(str(s).split()).lower()


def check_answer(problem: Problem, answer: str) -> Report:
    report = Report(problem.kind, hidden=True)
    data = problem.data
    explain = data.get("explain", "")
    if problem.kind == "quiz":
        try:
            choice = int(answer) - 1
        except ValueError:
            report.correct = False
            report.message = "Answer with the option number."
            return report
        report.correct = choice == int(data["answer"])
    else:
        accepted = data.get("answers") or [data["answer"]]
        report.correct = _norm(answer) in {_norm(a) for a in accepted}
    report.message = explain if report.correct else data.get("wrong", "Re-read the lesson (^l) or take a hint (h).")
    return report
