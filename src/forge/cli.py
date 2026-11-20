"""forge command line. With no subcommand, opens the TUI."""

from __future__ import annotations

import argparse
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.text import Text

from . import workspace
from .render import problem_label, report_text, stars
from .session import Session

console = Console()


def cmd_list(s: Session, a) -> None:
    console.print(Text(f"{s.course.title}   ★ {s.progress.total_stars()}", "bold"))
    for ch in s.course.chapters:
        console.print(Text(f"\n{ch.id:>2} {ch.title}", "bold cyan"))
        for part in ch.parts:
            console.print(Text(f"   {part.id} {part.title}", "bold"))
            for p in part.problems:
                console.print(Text("      ") + problem_label(p, s.progress.get(p.id)))


def cmd_open(s, a):
    p = s.open(a.id)
    console.rule(f"{p.id} · {p.title}  ({p.kind}, {p.difficulty})")
    console.print(Markdown(p.description()))
    if p.kind == "quiz":
        for i, c in enumerate(p.data.get("choices", []), 1):
            console.print(f"  {i}. {c}")
    elif p.kind == "code":
        for f in workspace.edit_paths(p):
            console.print(Text(f"edit: {f}", "cyan"))
    for i, h in enumerate(s.revealed_hints(p), 1):
        console.print(Text(f"\nhint {i}: ", "yellow") + Text(h))


def cmd_run(s, a, submit=False):
    p = s.resolve(a.id)
    if p.kind != "code":
        console.print(f"{p.id} is a {p.kind} problem: use `forge answer`")
        return 1
    rep, st = s.submit(p) if submit else (s.run(p), None)
    console.print(report_text(rep, st.attempts if st is not None else 0))
    if st is not None and rep.passed:
        console.print(Text(f"solved {p.id}  {stars(st)}", "bold yellow"))
    return 0 if rep.passed else 1


def cmd_answer(s, a):
    p = s.resolve(a.id)
    if p.kind == "code":
        console.print("this is a code problem: use `forge run` / `forge submit`")
        return 1
    rep, _ = s.answer(p, a.answer)
    console.print(report_text(rep))
    return 0 if rep.passed else 1


def cmd_hint(s, a):
    p = s.resolve(a.id)
    n, hints = s.next_hint(p)
    if not hints:
        console.print("no hints for this problem")
    for i, h in enumerate(hints[:n], 1):
        console.print(Text(f"hint {i}/{len(hints)}: ", "yellow") + Text(h))


def cmd_solution(s, a):
    console.print(Text("(marks this problem as assisted: 0 stars)\n", "dim"))
    console.print(s.solution_text(s.resolve(a.id)))


def cmd_reset(s, a):
    p = s.resolve(a.id)
    s.reset(p)
    console.print(f"restored starter files in {workspace.problem_dir(p)}")


def cmd_check(s, a):
    from .check import check_course
    return check_course(s.course, a.id)


def cmd_tui(s, a):
    from .tui.app import ForgeApp
    ForgeApp(s).run()


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="forge", description="Learn by building, in the terminal.")
    ap.add_argument("--course", default="c-compiler")
    sub = ap.add_subparsers(dest="cmd")

    def add(name, fn, help):
        p = sub.add_parser(name, help=help)
        p.add_argument("id", nargs="?", help="problem id, e.g. 0.1-03 (default: current)")
        p.set_defaults(fn=fn)
        return p

    add("list", cmd_list, "show the course tree")
    add("open", cmd_open, "make a problem current and show it")
    add("run", cmd_run, "run visible tests")
    add("submit", lambda s, a: cmd_run(s, a, submit=True), "run all tests and record the result")
    ans = sub.add_parser("answer", help="answer a quiz/predict problem")
    ans.add_argument("answer")
    ans.add_argument("id", nargs="?")
    ans.set_defaults(fn=cmd_answer)
    add("hint", cmd_hint, "reveal the next hint")
    add("solution", cmd_solution, "show the reference solution")
    add("reset", cmd_reset, "restore starter code")
    add("check", cmd_check, "validate course content (optional id prefix)")

    a = ap.parse_args(argv)
    fn = getattr(a, "fn", cmd_tui)
    return fn(Session(a.course), a) or 0


if __name__ == "__main__":
    sys.exit(main())
