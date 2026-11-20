"""Course content model: course → chapters → parts → problems, loaded from a directory tree.

    courses/<course>/course.toml
    courses/<course>/chapters/NN-slug/chapter.toml
    courses/<course>/chapters/NN-slug/NN-slug/{part.toml, lesson.md}
    courses/<course>/chapters/NN-slug/NN-slug/problems/NN-slug/{problem.toml, README.md, hints.md,
                                                               starter/, solution/, tests/}
IDs are derived from directory prefixes: chapter 0, part 0.1, problem 0.1-02.
"""

from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

KINDS = {"quiz", "predict", "code"}


def _num(path: Path) -> int:
    return int(path.name.split("-", 1)[0])


def _toml(path: Path) -> dict:
    return tomllib.loads(path.read_text()) if path.exists() else {}


@dataclass
class Problem:
    id: str
    dir: Path
    data: dict
    part: "Part" = field(repr=False)

    @property
    def title(self) -> str:
        return self.data.get("title", self.dir.name)

    @property
    def kind(self) -> str:
        return self.data.get("kind", "code")

    @property
    def difficulty(self) -> str:
        return self.data.get("difficulty", "easy")

    @property
    def challenge(self) -> bool:
        return bool(self.data.get("challenge", False))

    @property
    def mode(self) -> str:
        """drill: standalone files in drills/<id>/.  project: files in your growing compiler, project/."""
        return self.data.get("mode", "drill")

    @property
    def course(self) -> "Course":
        return self.part.chapter.course

    @property
    def werror(self) -> bool:
        return bool(self.data.get("werror", self.part.chapter.data.get("werror", False)))

    @property
    def e2e(self) -> list[dict]:
        """End-to-end cases: compile `source` with your compiler (or assemble your .s), run, compare."""
        return list(self.data.get("e2e", []))

    @property
    def has_unit_tests(self) -> bool:
        return (self.dir / "tests" / "visible.c").exists()

    @property
    def edit_files(self) -> list[str]:
        return list(self.data.get("files", {}).get("edit", []))

    @property
    def starter_dir(self) -> Path:
        return self.dir / "starter"

    @property
    def solution_dir(self) -> Path:
        return self.dir / "solution"

    def test_files(self, hidden: bool) -> list[Path]:
        if not self.has_unit_tests:
            return []
        files = [self.dir / "tests" / "visible.c"]
        if hidden and (self.dir / "tests" / "hidden.c").exists():
            files.append(self.dir / "tests" / "hidden.c")
        return files

    def description(self) -> str:
        readme = self.dir / "README.md"
        if readme.exists():
            return readme.read_text()
        return self.data.get("prompt", "")

    def hints(self) -> list[str]:
        path = self.dir / "hints.md"
        if not path.exists():
            return []
        return [h.strip() for h in path.read_text().split("\n---\n") if h.strip()]


@dataclass
class Part:
    id: str
    dir: Path
    data: dict
    chapter: "Chapter" = field(repr=False)
    problems: list[Problem] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.data.get("title", self.dir.name)

    def lesson(self) -> str:
        path = self.dir / "lesson.md"
        return path.read_text() if path.exists() else f"# {self.title}\n"


@dataclass
class Chapter:
    id: str
    dir: Path
    data: dict
    parts: list[Part] = field(default_factory=list)
    course: "Course" = field(default=None, repr=False)  # type: ignore[assignment]

    @property
    def title(self) -> str:
        return self.data.get("title", self.dir.name)


@dataclass
class Course:
    id: str
    dir: Path
    data: dict
    chapters: list[Chapter] = field(default_factory=list)

    @property
    def title(self) -> str:
        return self.data.get("title", self.id)

    @property
    def harness_dir(self) -> Path:
        return self.dir / "harness"

    @property
    def scaffold_dir(self) -> Path:
        """The initial project (your compiler) for project-mode problems."""
        return self.dir / "scaffold"

    def problems(self) -> list[Problem]:
        return [p for c in self.chapters for part in c.parts for p in part.problems]

    def find(self, pid: str) -> Problem:
        for p in self.problems():
            if p.id == pid:
                return p
        raise KeyError(f"no problem {pid!r} in course {self.id}")

    def neighbor(self, pid: str, step: int) -> Problem | None:
        probs = self.problems()
        idx = [p.id for p in probs].index(pid) + step
        return probs[idx] if 0 <= idx < len(probs) else None


def load_course(course_dir: Path) -> Course:
    course = Course(course_dir.name, course_dir, _toml(course_dir / "course.toml"))
    chapters_dir = course_dir / "chapters"
    for cdir in sorted(d for d in chapters_dir.iterdir() if d.is_dir()):
        chapter = Chapter(str(_num(cdir)), cdir, _toml(cdir / "chapter.toml"), course=course)
        for pdir in sorted(d for d in cdir.iterdir() if d.is_dir()):
            part = Part(f"{chapter.id}.{_num(pdir)}", pdir, _toml(pdir / "part.toml"), chapter)
            probs_dir = pdir / "problems"
            if probs_dir.exists():
                for qdir in sorted(d for d in probs_dir.iterdir() if d.is_dir()):
                    pid = f"{part.id}-{_num(qdir):02d}"
                    part.problems.append(Problem(pid, qdir, _toml(qdir / "problem.toml"), part))
            chapter.parts.append(part)
        course.chapters.append(chapter)
    return course
