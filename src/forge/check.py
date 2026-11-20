"""`forge check`: validate a course. Reference solutions must pass every test; starters must
compile and fail at least one test. Run this after writing or generating content."""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

from .course import KINDS, Course, Problem
from .runner import run_code
from .workspace import materialize, project_files


def _with_files(problem: Problem, use_solution: bool) -> Path:
    """A drill: starter (+ solution). A project problem: scaffold + reference solutions of all earlier
    project problems (+ this one's)."""
    d = Path(tempfile.mkdtemp(prefix="forge-check-"))
    if problem.mode == "project":
        materialize(project_files(problem, include_self=use_solution), d)
        return d
    shutil.copytree(problem.starter_dir, d, dirs_exist_ok=True)
    if use_solution:
        for f in problem.edit_files:
            shutil.copy2(problem.solution_dir / f, d / f)
    return d


def check_problem(course: Course, p: Problem) -> list[str]:
    errs: list[str] = []
    if p.kind not in KINDS:
        return [f"unknown kind {p.kind!r}"]
    if p.kind == "quiz":
        choices = p.data.get("choices", [])
        if not choices or not 0 <= int(p.data.get("answer", -1)) < len(choices):
            errs.append("quiz needs choices and a valid 0-based answer")
        return errs
    if p.kind == "predict":
        if "answer" not in p.data and "answers" not in p.data:
            errs.append("predict needs answer")
        return errs

    starters = [] if p.mode == "project" else [f"starter/{f}" for f in p.edit_files]
    for need in ["README.md", *starters, *[f"solution/{f}" for f in p.edit_files]]:
        if not (p.dir / need).exists():
            errs.append(f"missing {need}")
    if not p.has_unit_tests and not p.e2e:
        errs.append("needs tests/visible.c or [[e2e]] cases")
    if p.e2e and not any(not c.get("hidden") for c in p.e2e) and not p.has_unit_tests:
        errs.append("needs at least one visible test")
    if not p.edit_files:
        errs.append("files.edit is empty")
    if errs:
        return errs

    d = _with_files(p, use_solution=True)
    rep = run_code(course, p, d, hidden=True)
    shutil.rmtree(d, ignore_errors=True)
    if not rep.compiled:
        errs.append("solution does not compile:\n" + rep.compile_output)
    elif not rep.passed:
        bad = [f"{r.name}={r.status}" for r in rep.results if r.status != "pass"]
        errs.append(f"solution fails: {', '.join(bad) or 'no tests ran'}")
    elif rep.compile_output.strip():
        errs.append("solution has warnings:\n" + rep.compile_output)

    d = _with_files(p, use_solution=False)
    rep = run_code(course, p, d, hidden=True)
    shutil.rmtree(d, ignore_errors=True)
    if not rep.compiled:
        errs.append("starter does not compile:\n" + rep.compile_output)
    elif rep.passed:
        errs.append("starter already passes all tests")
    return errs


def check_course(course: Course, only: str | None = None) -> int:
    failures = 0
    for p in course.problems():
        if only and not p.id.startswith(only):
            continue
        errs = check_problem(course, p)
        mark = "ok " if not errs else "ERR"
        print(f"{mark} {p.id:8} {p.kind:8} {p.title}")
        for e in errs:
            print("      " + e.replace("\n", "\n      "))
        failures += bool(errs)
    print(f"\n{failures} problem(s) with errors" if failures else "\nall problems ok")
    return 1 if failures else 0
