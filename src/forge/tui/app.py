"""The forge TUI: course tree | problem/lesson | built-in vim, with a test panel underneath."""

from __future__ import annotations

import time

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Footer, Input, Markdown, Static, Tree

from .. import workspace
from ..course import Part, Problem
from ..render import problem_label, report_text, stars
from ..session import Session
from .vim import Vim

def _split_meta_keys() -> None:
    """Make ESC+key arrive as `escape` then `key`, like vim.

    Typing `Esc` then `:` or `j` quickly (or through tmux's escape-time) delivers both bytes in one
    read; Textual then reports `alt+j`, or drops the ESC entirely for punctuation (`:`), so vim
    seemed to ignore Esc. forge has no alt bindings, so always split. Patches a private Textual API
    (checked against textual 8.2.8)."""
    from textual import _xterm_parser, events

    cls = _xterm_parser.XTermParser
    if getattr(cls, "_forge_split", False):
        return
    orig = cls._sequence_to_key_events

    def split(self, sequence, alt=False):
        if alt:
            yield events.Key("escape", "\x1b")
        yield from orig(self, sequence, False)

    cls._sequence_to_key_events = split
    cls._forge_split = True


class _MainScreen(Screen):
    def on_resize(self) -> None:
        if self.app.is_mounted:
            self.app._relayout()


class ForgeApp(App):
    TITLE = "forge"
    ENABLE_COMMAND_PALETTE = False
    # Layout adapts to the terminal (see _relayout):
    #   wide    tree | doc | editor
    #   narrow  tree is a drawer (t); doc stacked above the editor
    #   quiz/predict problems have no editor and no test panel.
    TREE_W = 34
    CSS = """
    #topbar { height: 1; background: $primary-background; color: $text; padding: 0 1; }
    #main { height: 1fr; }
    #nav { width: 34; border-right: solid $primary-background-lighten-2; }
    #work { width: 1fr; layout: horizontal; }
    #doc { width: 1fr; height: 1fr; padding: 0 1; scrollbar-size-vertical: 1; }
    #editor-pane { width: 1.3fr; height: 1fr; border-left: solid $primary-background-lighten-2; }
    #editor-pane:focus-within { border-left: solid $accent; }
    .-stack #work { layout: vertical; }
    .-stack #doc { width: 1fr; height: 45%; }
    .-stack #editor-pane { width: 1fr; height: 1fr; border-left: none;
                           border-top: solid $primary-background-lighten-2; }
    .-stack #editor-pane:focus-within { border-left: none; border-top: solid $accent; }
    .-notree #nav { display: none; }
    .-nocode #editor-pane, .-nocode #tests { display: none; }
    .-nocode #doc { height: 1fr; }
    .-nodoc #doc { display: none; }
    .-nodoc #editor-pane { border-left: none; border-top: none; }
    .-short #tests { height: 6; }
    #tests { height: 9; border-top: solid $primary-background-lighten-2; padding: 0 1; }
    #tests-title { height: 1; color: $text-muted; }
    #choices, #predict, #result { margin: 1 0 0 0; }
    #doc Markdown { margin: 0; padding: 0; }
    #doc MarkdownH2:first-child { margin: 0 0 1 0; }
    #doc MarkdownFence { overflow: hidden hidden; }
    #doc MarkdownFence > Label { width: 1fr; text-wrap: wrap; padding: 0 1; }
    .hidden { display: none; }
    """
    BINDINGS = [
        # ctrl keys work everywhere, even inside vim (priority beats the editor's key handling)
        Binding("ctrl+g", "toggle_focus", "edit", priority=True),
        Binding("ctrl+e", "run", "run", priority=True),
        Binding("ctrl+s", "submit", "submit", priority=True),
        Binding("ctrl+l", "lesson", "lesson", priority=True),
        Binding("ctrl+n", "next", "next", priority=True),
        Binding("ctrl+p", "prev", "prev", show=False, priority=True),
        Binding("ctrl+t", "toggle_tree", "tree", priority=True),
        Binding("ctrl+f", "toggle_doc", "focus", priority=True),
        Binding("ctrl+q", "quit", "quit", priority=True),
        # plain keys only when the editor/answer box isn't focused
        Binding("h", "hint", "hint", show=False),
        Binding("S", "solution", "solution", show=False),
        Binding("R", "reset", "reset", show=False),
        Binding("escape", "focus_nav", show=False),
        Binding("j", "scroll_doc(2)", show=False),
        Binding("k", "scroll_doc(-2)", show=False),
        Binding("space", "scroll_doc(10)", show=False),
        Binding("enter", "edit", show=False),
        *[Binding(str(i), f"answer({i})", show=False) for i in range(1, 10)],
    ]

    def __init__(self, session: Session):
        _split_meta_keys()
        super().__init__()
        self.s = session
        self.problem: Problem = session.open()
        self.showing_lesson = False
        self.tree_open: bool | None = None  # None = follow the screen width
        self.doc_hidden = False  # focus mode (^f): editor only, for code problems

    # -- layout -------------------------------------------------------------
    def compose(self) -> ComposeResult:
        yield Static(id="topbar")
        with Horizontal(id="main"):
            yield Tree(self.s.course.title, id="nav")
            with Vertical(id="work"):
                with VerticalScroll(id="doc"):
                    yield Markdown(id="desc")
                    yield Static(id="choices", classes="hidden")
                    yield Input(placeholder="your answer, then Enter", id="predict", classes="hidden")
                    yield Static(id="result")
                    yield Markdown(id="hints")
                with Vertical(id="editor-pane"):
                    yield Vim(id="vim")
        with Vertical(id="tests"):
            yield Static(id="tests-title")
            with VerticalScroll():
                yield Static(id="tests-body")
        yield Footer()

    def on_mount(self) -> None:
        self.build_tree()
        self.show_problem(self.problem)
        self._relayout()
        self.focus_home()
        self.s.activity.log("start", self.problem.id, size=[self.size.width, self.size.height])

    async def action_quit(self) -> None:
        self.vim.save_if_dirty()
        self.flush_editor()
        self.s.activity.log("quit", self.problem.id)
        self.exit()

    def get_default_screen(self) -> Screen:
        return _MainScreen(id="_default")

    def _relayout(self) -> None:
        w = self.size.width
        tree = self.tree_open if self.tree_open is not None else w >= 130
        avail = w - (self.TREE_W if tree else 0)
        scr = self.screen
        scr.set_class(not tree, "-notree")
        scr.set_class(avail < 110, "-stack")
        scr.set_class(self.size.height < 36, "-short")
        scr.set_class(self.problem.kind != "code", "-nocode")
        scr.set_class(self.doc_hidden and self.problem.kind == "code" and not self.showing_lesson, "-nodoc")
        self.update_topbar()
        if not tree and self.query_one("#nav").has_focus:
            self.focus_home()

    @property
    def tree_visible(self) -> bool:
        return not self.screen.has_class("-notree")

    def focus_home(self) -> None:
        """Focus the tree if it is showing, else the problem text."""
        if self.tree_visible:
            self.query_one("#nav").focus()
        elif self.screen.has_class("-nodoc"):
            self.vim.focus()  # focus mode: the editor is all there is
        else:
            self.query_one("#doc").focus()

    def action_toggle_doc(self) -> None:
        if self.problem.kind != "code":
            return
        self.doc_hidden = not self.doc_hidden
        self._relayout()
        if self.doc_hidden and not self.vim.has_focus:
            self.vim.focus()
        self.s.activity.log("focus_mode", self.problem.id, on=self.doc_hidden)

    def _show_doc(self) -> None:
        if self.doc_hidden:
            self.doc_hidden = False
            self._relayout()

    def action_toggle_tree(self) -> None:
        self.tree_open = not self.tree_visible
        self._relayout()
        if self.tree_open:
            tree = self.query_one("#nav", Tree)
            tree.focus()
            if (node := self._node_for(self.problem)) is not None:
                self.call_after_refresh(tree.move_cursor, node)
        else:
            self.focus_home()

    def build_tree(self) -> None:
        tree = self.query_one("#nav", Tree)
        tree.clear()
        tree.show_root = False
        for ch in self.s.course.chapters:
            cnode = tree.root.add(Text(f"{ch.id} {ch.title}", "bold"), expand=True)
            for part in ch.parts:
                pnode = cnode.add(Text(f"{part.id} {part.title}"), data=part, expand=True)
                for p in part.problems:
                    leaf = pnode.add_leaf(problem_label(p, self.s.progress.get(p.id)), data=p)
                    if p.id == self.problem.id:
                        self.call_after_refresh(tree.move_cursor, leaf)
        self.update_topbar()

    def refresh_tree_labels(self) -> None:
        tree = self.query_one("#nav", Tree)

        def walk(node):
            if isinstance(node.data, Problem):
                node.set_label(problem_label(node.data, self.s.progress.get(node.data.id)))
            for c in node.children:
                walk(c)

        walk(tree.root)
        self.update_topbar()

    def update_topbar(self) -> None:
        probs = self.s.course.problems()
        solved = sum(self.s.progress.get(p.id).status == "solved" for p in probs)
        t = Text()
        t.append("forge", "bold")
        t.append(f" · {self.s.course.title}   ")
        t.append(f"{solved}/{len(probs)} solved   ", "green")
        t.append(f"★ {self.s.progress.total_stars()}", "yellow")
        if not self.tree_visible:
            t.append(f"   {self.problem.id} {self.problem.title}", "dim")
        self.query_one("#topbar", Static).update(t)

    # -- content --------------------------------------------------------------
    def flush_editor(self) -> None:
        """Write the vim command trace for the current problem to the activity log."""
        if trace := self.vim.take_trace():
            self.s.activity.log("editor", self.problem.id, cmds=trace)

    def show_problem(self, p: Problem) -> None:
        self.vim.save_if_dirty()
        if p is not self.problem:
            self.flush_editor()
        self.problem = p
        self.showing_lesson = False
        self.s.open(p.id)
        tag = f"{p.kind} · {p.difficulty}" + (" · ★ challenge" if p.challenge else "")
        md = f"## {p.id} · {p.title}\n\n*{tag}*\n\n{p.description()}"
        if p.kind == "code":
            files = ", ".join(f"`{f}`" for f in p.edit_files)
            md += f"\n\n---\nEdit {files} — `:w` runs the example tests, `^s` submits."
        self.query_one("#desc", Markdown).update(md)

        choices = self.query_one("#choices", Static)
        predict = self.query_one("#predict", Input)
        choices.set_class(p.kind != "quiz", "hidden")
        predict.set_class(p.kind != "predict", "hidden")
        if p.kind == "quiz":
            t = Text()
            for i, c in enumerate(p.data.get("choices", []), 1):
                t.append(f"  {i}  ", "bold reverse")
                t.append(f"  {c}\n")
            t.append("\npress the number to answer", "dim")
            choices.update(t)
        if p.kind == "predict":
            predict.value = ""
        self.query_one("#result", Static).update("")
        self.show_hints()
        self.query_one("#doc").scroll_home(animate=False)

        self.set_tests_title()
        self.query_one("#tests-body", Static).update(Text(":w or ^e runs the example tests · ^s submits", "dim"))
        self.query_one("#tests").styles.height = None  # back to the CSS default
        if p.kind == "code":
            self.vim.open(workspace.edit_paths(p)[0])
        if self.is_mounted:
            self._relayout()
        self.update_topbar()

    def show_hints(self) -> None:
        hints = self.s.revealed_hints(self.problem)
        total = len(self.problem.hints())
        md = "\n\n".join(f"> 💡 **Hint {i}/{total}.** {h}" for i, h in enumerate(hints, 1))
        self.query_one("#hints", Markdown).update(md)

    def set_tests_title(self, extra: str = "") -> None:
        p = self.problem
        t = f"tests · {', '.join(p.edit_files)} · :w runs" + (f" · {extra}" if extra else "")
        self.query_one("#tests-title", Static).update(Text(t, "dim"))

    # -- editor -----------------------------------------------------------------
    @property
    def vim(self) -> Vim:
        return self.query_one("#vim", Vim)

    def action_toggle_focus(self) -> None:
        if self.vim.has_focus:
            self.focus_home()
        elif self.problem.kind == "code":
            self.vim.focus()

    def action_edit(self) -> None:
        if self.problem.kind == "code":
            self.vim.focus()
        elif self.problem.kind == "predict":
            self.query_one("#predict", Input).focus()

    @on(Vim.Quit)
    def vim_quit(self) -> None:
        self.focus_home()

    @on(Vim.Saved)
    def vim_saved(self) -> None:
        if self.problem.kind == "code":
            self.run_tests(self.problem, False)

    # -- tree events -----------------------------------------------------------
    @on(Tree.NodeHighlighted)
    def node_highlighted(self, ev: Tree.NodeHighlighted) -> None:
        data = ev.node.data
        if isinstance(data, Problem) and data is not self.problem:
            self.show_problem(data)
        elif isinstance(data, Part):
            self.show_lesson(data)

    @on(Tree.NodeSelected)
    def node_selected(self, ev: Tree.NodeSelected) -> None:
        data = ev.node.data
        if isinstance(data, Problem):
            if data is not self.problem:
                self.show_problem(data)
            if self.tree_open and self.size.width < 130:
                self.tree_open = None  # drawer: close after picking
                self._relayout()
            if data.kind == "code":
                self.vim.focus()
            elif data.kind == "predict":
                self.query_one("#predict", Input).focus()

    def show_lesson(self, part: Part) -> None:
        self.showing_lesson = True
        self.s.activity.log("lesson", part.id)
        self.query_one("#desc", Markdown).update(part.lesson())
        self.query_one("#choices").add_class("hidden")
        self.query_one("#predict").add_class("hidden")
        self.query_one("#result", Static).update("")
        self.query_one("#hints", Markdown).update("")
        self.query_one("#doc").scroll_home(animate=False)

    # -- actions ------------------------------------------------------------------
    def action_lesson(self) -> None:
        self._show_doc()
        if self.showing_lesson:
            self.show_problem(self.problem)
        else:
            self.show_lesson(self.problem.part)

    def _next_hint_text(self) -> str:
        has_next = self.s.course.neighbor(self.problem.id, 1) is not None
        return "   ^n for the next problem" if has_next else "   that's the last problem so far"

    def _goto(self, step: int) -> None:
        cur = self.query_one("#nav", Tree).cursor_node
        base = cur.data if cur is not None and isinstance(cur.data, Problem) else self.problem
        p = self.s.course.neighbor(base.id, step)
        if not p:
            self.notify("that's the last problem so far: more chapters are coming" if step > 0
                        else "this is the first problem")
            return
        node = self._node_for(p)
        if node is not None:
            self.query_one("#nav", Tree).move_cursor(node)  # NodeHighlighted → show_problem
        else:
            self.show_problem(p)

    def _node_for(self, p: Problem):
        def find(node):
            if node.data is p:
                return node
            for c in node.children:
                if (r := find(c)) is not None:
                    return r
        return find(self.query_one("#nav", Tree).root)

    def action_next(self) -> None:
        self._goto(1)

    def action_prev(self) -> None:
        self._goto(-1)

    def action_hint(self) -> None:
        self._show_doc()
        n, hints = self.s.next_hint(self.problem)
        if not hints:
            self.notify("no hints for this problem")
        elif self.s.progress.get(self.problem.id).status != "solved":
            st = self.s.progress.get(self.problem.id)
            self.notify(f"hint {n}/{len(hints)} revealed (max stars now {st.award()})")
        self.show_hints()
        self.query_one("#doc").scroll_end(animate=False)

    def action_answer(self, i: int) -> None:
        if self.problem.kind == "quiz" and not self.showing_lesson:
            self._grade(str(i))

    @on(Input.Submitted, "#predict")
    def predict_submitted(self, ev: Input.Submitted) -> None:
        if ev.value.strip():
            self._grade(ev.value)
            ev.input.value = ""

    def _grade(self, answer: str) -> None:
        rep, st = self.s.answer(self.problem, answer)
        body = report_text(rep)
        if rep.passed:
            body.append(f"\n\nsolved  {stars(st)}" + self._next_hint_text(), "bold yellow")
            self.focus_home()
        result = self.query_one("#result", Static)
        result.update(body)
        self.call_after_refresh(result.scroll_visible, animate=False)
        self.refresh_tree_labels()

    def action_scroll_doc(self, dy: int) -> None:
        doc = self.query_one("#doc")
        doc.scroll_relative(y=dy, animate=False)

    def action_focus_nav(self) -> None:
        self.focus_home()

    def action_run(self) -> None:
        if self.problem.kind == "code":
            self.vim.save_if_dirty()
            self.run_tests(self.problem, False)

    def action_submit(self) -> None:
        if self.problem.kind == "code":
            self.vim.save_if_dirty()
            self.run_tests(self.problem, True)

    def action_solution(self) -> None:
        self._show_doc()
        text = self.s.solution_text(self.problem)
        self.query_one("#hints", Markdown).update(f"**Reference solution** (problem marked assisted)\n\n```c\n{text}\n```")
        self.refresh_tree_labels()

    def action_reset(self) -> None:
        if self.problem.kind == "code":
            self.s.reset(self.problem)
            self.vim.open(workspace.edit_paths(self.problem)[0])
            self.notify("starter code restored")

    # -- test running --------------------------------------------------------------
    @work(thread=True, exclusive=True, group="tests")
    def run_tests(self, p: Problem, submit: bool) -> None:
        self.call_from_thread(self.set_tests_title, "submitting…" if submit else "running…")
        t0 = time.monotonic()
        if submit:
            rep, st = self.s.submit(p)
        else:
            rep, st = self.s.run(p), None
        dt = time.monotonic() - t0
        self.call_from_thread(self._show_report, p, rep, st, dt)

    def _fit_tests(self, body: Text) -> None:
        """Grow the test pane to fit the report (title + border + lines), up to 45% of the screen."""
        pane = self.query_one("#tests")
        width = max(pane.size.width - 3, 20)
        rows = sum(max(1, -(-len(ln) // width)) for ln in body.plain.rstrip("\n").split("\n"))
        base = 6 if self.screen.has_class("-short") else 9
        pane.styles.height = max(base, min(rows + 2, int(self.size.height * 0.45)))

    def _show_report(self, p: Problem, rep, st, dt: float) -> None:
        if p is not self.problem:
            return
        body = report_text(rep, st.attempts if st is not None else 0)
        if st is not None and rep.passed:
            body.append(f"\nsolved  {stars(st)}" + self._next_hint_text(), "bold yellow")
            self.notify(f"Accepted {stars(st)}", title=p.title)
            self.refresh_tree_labels()
        elif st is not None:
            self.refresh_tree_labels()
        self.query_one("#tests-body", Static).update(body)
        self._fit_tests(body)
        self.set_tests_title(f"{'submit' if st is not None else 'run'} {dt:.1f}s · {rep.summary}")
