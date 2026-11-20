"""A learning session: one course + the user's progress. Shared by the CLI and the TUI."""

from __future__ import annotations

from . import config, runner, workspace
from .activity import Activity
from .course import Course, Problem, load_course
from .progress import Progress


class Session:
    def __init__(self, course_id: str = "c-compiler"):
        self.course: Course = load_course(config.COURSES_DIR / course_id)
        self.progress = Progress.load(self.course.id)
        self.activity = Activity(self.course.id)

    # -- navigation -------------------------------------------------------
    def current(self) -> Problem:
        if self.progress.current:
            try:
                return self.course.find(self.progress.current)
            except KeyError:
                pass
        return self.first_unsolved()

    def first_unsolved(self) -> Problem:
        for p in self.course.problems():
            if self.progress.get(p.id).status != "solved":
                return p
        return self.course.problems()[0]

    def open(self, pid: str | None = None) -> Problem:
        problem = self.course.find(pid) if pid else self.current()
        self.activity.opened(problem.id)
        self.progress.current = problem.id
        self.progress.save()
        workspace.ensure(problem)
        return problem

    def resolve(self, pid: str | None) -> Problem:
        return self.course.find(pid) if pid else self.current()

    # -- actions ----------------------------------------------------------
    def run(self, problem: Problem, hidden: bool = False, _ev: str = "run") -> runner.Report:
        src = workspace.ensure(problem)
        report = runner.run_code(self.course, problem, src, hidden)
        self._log_code_result(_ev, problem, report)
        return report

    def submit(self, problem: Problem) -> tuple[runner.Report, object]:
        report = self.run(problem, hidden=True, _ev="submit")
        state = self.progress.record_submit(problem.id, report.passed)
        if report.passed:
            self.activity.log("solved", problem.id, stars=state.stars, attempts=state.attempts,
                              hints=state.hints, secs=self.activity.seconds_on(problem.id))
        return report, state

    def answer(self, problem: Problem, answer: str) -> tuple[runner.Report, object]:
        report = runner.check_answer(problem, answer)
        state = self.progress.record_submit(problem.id, report.passed, penalize=True)
        self.activity.log("answer", problem.id, answer=answer, correct=report.passed,
                          secs=self.activity.seconds_on(problem.id))
        return report, state

    def _log_code_result(self, ev: str, problem: Problem, report: runner.Report) -> None:
        files = {}
        for f in problem.edit_files:
            try:
                files[f] = (workspace.problem_dir(problem) / f).read_text()
            except OSError:
                pass
        fails = [{k: v for k, v in vars(r).items() if v not in (None, "", False) and k not in ("source", "mark")}
                 for r in report.results if r.status != "pass"]
        for r in fails:
            r["output"] = r.get("output", "")[:600]
        rec = {"summary": report.summary, "passed": report.passed,
               "n_pass": sum(r.status == "pass" for r in report.results), "n": len(report.results)}
        if report.compile_output:
            rec["compiler"] = report.compile_output[:2000]
        if fails:
            rec["fails"] = fails[:5]
        if (code := self.activity.code_if_changed(problem.id, files)) is not None:
            rec["code"] = code
        self.activity.log(ev, problem.id, **rec)

    def next_hint(self, problem: Problem) -> tuple[int, list[str]]:
        """Reveal one more hint. Returns (revealed_count, all_hints)."""
        hints = problem.hints()
        st = self.progress.get(problem.id)
        if st.hints < len(hints) and st.status != "solved":
            st.hints += 1
            self.progress.save()
            self.activity.log("hint", problem.id, n=st.hints, of=len(hints),
                              secs=self.activity.seconds_on(problem.id))
        return min(st.hints, len(hints)), hints

    def revealed_hints(self, problem: Problem) -> list[str]:
        return problem.hints()[: self.progress.get(problem.id).hints]

    def mark_assisted(self, problem: Problem) -> None:
        st = self.progress.get(problem.id)
        if st.status != "solved":
            st.assisted = True
            self.progress.save()

    def solution_text(self, problem: Problem) -> str:
        self.mark_assisted(problem)
        self.activity.log("solution", problem.id, secs=self.activity.seconds_on(problem.id))
        if problem.kind != "code":
            return problem.data.get("explain", "")
        parts = []
        for f in problem.edit_files:
            parts.append(f"// ---- {f} ----\n" + (problem.solution_dir / f).read_text())
        return "\n".join(parts)

    def reset(self, problem: Problem) -> None:
        self.activity.log("reset", problem.id)
        workspace.reset(problem)
