"""The user's workspace, ~/forge-work/<course>/:

    drills/<problem-id>/   one standalone directory per drill, copied from its starter/
    project/               your compiler, shared by every project-mode problem, started from scaffold/

Files are created on first open and never overwritten, except by an explicit reset.
"""

from __future__ import annotations

import shutil
from pathlib import Path

from . import config
from .course import Course, Problem


def course_root(course_id: str) -> Path:
    root = config.WORK_DIR / course_id
    root.mkdir(parents=True, exist_ok=True)
    return root


def problem_dir(problem: Problem) -> Path:
    root = course_root(problem.course.id)
    return root / "project" if problem.mode == "project" else root / "drills" / problem.id


def _scaffold_files(course: Course) -> dict[str, Path]:
    sd = course.scaffold_dir
    return {str(f.relative_to(sd)): f for f in sorted(sd.rglob("*")) if f.is_file()} if sd.exists() else {}


def project_files(problem: Problem, include_self: bool) -> dict[str, Path]:
    """Where each project file comes from just before (or after) solving `problem` with the reference
    solutions: scaffold, then every earlier project problem's solution, then this problem's starters for
    files that don't exist yet. Used by `forge check`; a learner's own project is never rebuilt this way."""
    files = _scaffold_files(problem.course)
    for p in problem.course.problems():
        if p.mode != "project":
            continue
        if p is problem and not include_self:
            break
        for f in p.edit_files:
            if (p.solution_dir / f).exists():
                files[f] = p.solution_dir / f
        if p is problem:
            break
    for f in problem.edit_files:
        if f not in files and (problem.starter_dir / f).exists():
            files[f] = problem.starter_dir / f
    return files


def materialize(files: dict[str, Path], dest: Path) -> None:
    for rel, src in files.items():
        (dest / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dest / rel)


def _starter_for(problem: Problem, f: str) -> Path | None:
    if (problem.starter_dir / f).exists():
        return problem.starter_dir / f
    return _scaffold_files(problem.course).get(f)


def ensure(problem: Problem) -> Path:
    """Create the problem's workspace (no-op for files that exist)."""
    d = problem_dir(problem)
    if problem.kind != "code":
        return d
    if problem.mode == "project":
        if not d.exists():
            materialize(_scaffold_files(problem.course), d)
        for f in problem.edit_files:
            if not (d / f).exists() and (src := _starter_for(problem, f)) is not None:
                materialize({f: src}, d)
    elif not d.exists():
        shutil.copytree(problem.starter_dir, d)
    return d


def edit_paths(problem: Problem) -> list[Path]:
    d = ensure(problem)
    return [d / f for f in problem.edit_files]


def reset(problem: Problem) -> None:
    """Restore the starter files. In the project, the old file is kept as <file>.bak first, because
    a project file can also hold your solutions to other problems."""
    d = problem_dir(problem)
    for f in problem.edit_files:
        src = _starter_for(problem, f) if problem.mode == "project" else problem.starter_dir / f
        if src is None:
            continue
        if problem.mode == "project" and (d / f).exists():
            shutil.copy2(d / f, d / (f + ".bak"))
        materialize({f: src}, d)
