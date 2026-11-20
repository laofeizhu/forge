"""User progress, stored as JSON in DATA_DIR/<course>.json. Content dirs stay read-only."""

from __future__ import annotations

import json
import time
from dataclasses import asdict, dataclass, field

from . import config


@dataclass
class ProblemState:
    status: str = "new"  # new | attempted | solved
    hints: int = 0  # hints revealed
    attempts: int = 0  # submits
    assisted: bool = False  # viewed or adopted the reference solution
    stars: int = 0
    solved_at: float | None = None
    wrong: int = 0  # wrong quiz/predict answers (code submits are not penalized)

    def award(self) -> int:
        if self.assisted:
            return 0
        return max(1, 3 - self.hints - self.wrong)


@dataclass
class Progress:
    course: str
    current: str | None = None
    problems: dict[str, ProblemState] = field(default_factory=dict)

    @property
    def path(self):
        return config.DATA_DIR / f"{self.course}.json"

    @classmethod
    def load(cls, course: str) -> "Progress":
        prog = cls(course)
        if prog.path.exists():
            raw = json.loads(prog.path.read_text())
            prog.current = raw.get("current")
            prog.problems = {k: ProblemState(**v) for k, v in raw.get("problems", {}).items()}
        return prog

    def save(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        raw = {"current": self.current, "problems": {k: asdict(v) for k, v in self.problems.items()}}
        self.path.write_text(json.dumps(raw, indent=2))

    def get(self, pid: str) -> ProblemState:
        return self.problems.setdefault(pid, ProblemState())

    def record_submit(self, pid: str, passed: bool, penalize: bool = False) -> ProblemState:
        st = self.get(pid)
        st.attempts += 1
        if not passed and penalize and st.status != "solved":
            st.wrong += 1
        if passed:
            if st.status != "solved":
                st.solved_at = time.time()
            st.stars = max(st.stars, st.award())
            st.status = "solved"
        elif st.status == "new":
            st.status = "attempted"
        self.save()
        return st

    def total_stars(self) -> int:
        return sum(s.stars for s in self.problems.values())
