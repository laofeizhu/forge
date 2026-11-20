"""Rich renderables for test reports and the course tree (used by CLI and TUI)."""

from __future__ import annotations

import re

from rich.text import Text

from .course import Problem
from .progress import ProblemState
from .runner import Report

ICON = {"pass": ("✓", "green"), "fail": ("✗", "red"), "crash": ("💥", "red"), "timeout": ("⏱", "yellow")}


def status_icon(st: ProblemState) -> tuple[str, str]:
    if st.status == "solved":
        return "✓", "green"
    if st.status == "attempted":
        return "◐", "yellow"
    return "·", "dim"


def stars(st: ProblemState) -> str:
    if st.status != "solved":
        return ""
    return "★" * st.stars + "☆" * (3 - st.stars)


def problem_label(p: Problem, st: ProblemState) -> Text:
    icon, style = status_icon(st)
    t = Text()
    t.append(f"{icon} ", style)
    t.append(f"{p.id.split('-')[1]} {p.title}")
    if p.challenge:
        t.append(" ★", "magenta")
    if st.status == "solved":
        t.append(f"  {stars(st)}", "yellow")
    return t


def _esc(v) -> str:
    """Show invisible characters in expected/got: a trailing newline matters."""
    return str(v).replace("\n", "\\n").replace("\t", "\\t").replace("\r", "\\r")


def _first_lines(s: str, n: int) -> str:
    lines = s.rstrip().splitlines()
    return "\n".join(lines[:n]) + (f"\n… ({len(lines) - n} more lines)" if len(lines) > n else "")


HARNESS_FRAMES = ("forge_test.c", "dyld", "libsystem", "libclang_rt", "<unknown")


def condense_crash(output: str) -> str:
    """Keep the parts of a sanitizer report a learner needs: what, where (their frames), which object."""
    if "Sanitizer" not in output and "runtime error" not in output:
        return output
    keep: list[str] = []
    seen: set[str] = set()
    for line in output.splitlines():
        s = line.strip()
        if "ERROR: AddressSanitizer" in s:
            keep.append(re.sub(r" on address 0x[0-9a-f]+.*", "", s.split("ERROR: ", 1)[1]))
        elif re.match(r"(READ|WRITE) of size", s):
            keep.append(re.sub(r" at 0x[0-9a-f]+", "", s.split(" thread")[0]))
        elif "runtime error:" in s:
            keep.append(s)
        elif re.match(r"#\d+ 0x[0-9a-f]+ in ", s):
            frame = re.sub(r"#\d+ 0x[0-9a-f]+ in ", "", s)
            fn = frame.split()[0]
            if not any(h in s for h in HARNESS_FRAMES) and fn not in seen:
                seen.add(fn)
                keep.append("  at " + frame)
        elif "<== Memory access" in s:
            keep.append("  object " + s.split("<==")[0].strip() + "  ← " + s.split("<== ")[1])
        elif s.startswith("freed by thread") or s.startswith("previously allocated by"):
            keep.append(s.split(" here")[0] + ":")
    return "\n".join(keep) if keep else output


def report_text(report: Report, attempts: int = 0) -> Text:
    """attempts: submits so far, including this one (adds a nudge after repeated failed submits)."""
    t = Text()
    if report.kind != "code":
        if report.correct:
            t.append("✓ Correct! ", "bold green")
        else:
            t.append("✗ Not quite. ", "bold red")
        t.append(report.message)
        return t

    if not report.compiled:
        t.append("✗ Compile error\n", "bold red")
        t.append(_first_lines(report.compile_output, 30))
        return t

    for r in report.results:
        icon, style = ICON.get(r.status, ("?", "red"))
        t.append(f"{icon} ", style)
        t.append(r.name, "bold" if r.status != "pass" else "")
        if r.hidden:
            t.append(" (hidden)", "dim")
        if r.status == "fail":
            t.append(f"   line {r.line}: " if r.line else "   ", "dim")
            t.append(f"{r.expr}\n", "cyan")
            t.append("    expected ", "dim")
            t.append(_esc(r.expected), "green")
            t.append("   got ", "dim")
            t.append(_esc(r.got), "red")
        elif r.status == "crash":
            why = "sanitizer error" if "Sanitizer" in r.output or "runtime error" in r.output else (r.signal or "nonzero exit")
            t.append(f"   crashed ({why})", "red")
        elif r.status == "timeout":
            t.append("   timed out — infinite loop?", "yellow")
        t.append("\n")
        if r.source and r.status != "pass":
            body = [ln for _, ln in r.source]
            ind = min((len(ln) - len(ln.lstrip()) for ln in body if ln.strip()), default=0)
            for no, ln in r.source:
                hit = no == r.mark
                t.append("  ▶ " if hit else "    ", "red" if hit else "dim")
                t.append(f"{no:>3}  ", "dim")
                t.append(ln[ind:] + "\n", "bold" if hit else "")
        if r.output.strip():  # failures, and your own fprintf(stderr, ...) on passing tests
            for line in _first_lines(condense_crash(r.output), 20).splitlines():
                t.append(f"    │ {line}\n", "dim")

    passed = sum(r.status == "pass" for r in report.results)
    total = len(report.results)
    if report.passed:
        t.append(f"\n{'Accepted' if report.hidden else 'All visible tests pass'} — {passed}/{total}", "bold green")
        if not report.hidden:
            t.append("   (submit to run hidden tests)", "dim")
    else:
        t.append(f"\n{passed}/{total} tests passed", "bold red")
        if report.hidden and attempts >= 2 and report.compiled:
            t.append("\nbefore submitting again: turn a failing test's name into an input and trace it "
                     "by hand (or add one fprintf)", "yellow")
    if report.compile_output.strip():
        t.append("\n\nwarnings:\n", "yellow")
        t.append(_first_lines(report.compile_output, 15), "dim")
    return t
