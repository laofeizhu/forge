"""A deliberately small vim: one buffer, no syntax highlighting.

Normal   h j k l  w b e  0 ^ $  gg G  ctrl+d ctrl+u   (counts work: 3j, 2dd, 5G)
         i a I A o O   x X r<c> J   dd cc yy D C   d/c/y + w e b 0 $   p P   u ctrl+r
Insert   type; enter (auto-indent), backspace, tab (4 spaces), arrows, esc
Command  :w  :q  :wq  :x  :<line>
C syntax highlighting is a per-line regex tokenizer (block-comment state carried across lines).
"""

from __future__ import annotations

import re
from pathlib import Path

from rich.segment import Segment
from rich.style import Style
from textual import events
from textual.message import Message
from textual.strip import Strip
from textual.widget import Widget

INDENT = "    "
NUM = Style(dim=True)
CURSOR = Style(reverse=True)
STATUS = Style(reverse=True)
LABEL = Style(color="black", bgcolor="magenta", bold=True)
SEEK_LABELS = "asdfghjklqwertyuiopzxcvbnmASDFGHJKLQWERTYUIOPZXCVBNM"

KEYWORDS = set("""auto break case const continue default do else enum extern for goto if inline
register restrict return sizeof static struct switch typedef union volatile while""".split())
TYPES = set("""void char short int long float double signed unsigned _Bool bool size_t ssize_t
uintptr_t intptr_t int8_t int16_t int32_t int64_t uint8_t uint16_t uint32_t uint64_t FILE
va_list NULL true false""".split())
HL = {
    "comment": Style(color="bright_black", italic=True),
    "string": Style(color="green"),
    "number": Style(color="yellow"),
    "keyword": Style(color="magenta", bold=True),
    "type": Style(color="cyan"),
    "pre": Style(color="blue"),
}
TOKEN = re.compile(r"""(?P<lc>//.*)|(?P<bc>/\*)|(?P<string>"(?:\\.|[^"\\])*"?|'(?:\\.|[^'\\])*'?)
    |(?P<number>\b(?:0[xX][0-9a-fA-F]+|\d+)[uUlL]*\b)|(?P<word>[A-Za-z_]\w*)""", re.X)


def highlight(line: str, in_comment: bool) -> tuple[list[Style | None], bool]:
    """Per-character styles for one line, and whether a /* comment is still open at its end."""
    styles: list[Style | None] = [None] * len(line)
    if not in_comment and line.lstrip().startswith("#"):
        return [HL["pre"]] * len(line), False
    i = 0
    while i < len(line):
        if in_comment:
            end = line.find("*/", i)
            stop = len(line) if end < 0 else end + 2
            styles[i:stop] = [HL["comment"]] * (stop - i)
            i, in_comment = stop, end < 0
            continue
        m = TOKEN.search(line, i)
        if not m:
            break
        kind, (a, b) = m.lastgroup, m.span()
        if kind == "bc":
            i, in_comment = a, True
            continue
        if kind == "lc":
            kind = "comment"
        elif kind == "word":
            kind = "keyword" if m.group() in KEYWORDS else "type" if m.group() in TYPES else None
        if kind:
            styles[a:b] = [HL[kind]] * (b - a)
        i = b
    return styles, in_comment


def _cls(ch: str) -> int:
    """Character class for word motions: 0 space, 1 word, 2 punctuation."""
    if ch.isspace():
        return 0
    return 1 if ch.isalnum() or ch == "_" else 2


def _indent(line: str) -> str:
    return line[: len(line) - len(line.lstrip(" "))]


class Vim(Widget, can_focus=True):
    DEFAULT_CSS = "Vim { height: 1fr; width: 1fr; }"

    class Quit(Message):
        """:q — the app moves focus back to the course tree."""

    class Saved(Message):
        """:w — the app re-runs the visible tests."""

    def __init__(self, **kw):
        super().__init__(**kw)
        self.path: Path | None = None
        self.lines = [""]
        self.row = self.col = 0
        self.top = self.left = 0
        self.mode = "normal"  # normal | insert | command
        self.pending = ""  # partial normal-mode command, e.g. "2d"
        self.cmd = ""
        self.msg = ""
        self.reg: tuple[list[str], bool] = ([], False)  # (text, linewise)
        self.undo: list[tuple[list[str], int, int]] = []
        self.redo: list[tuple[list[str], int, int]] = []
        self.dirty = False
        self.last_find: tuple[str, str] | None = None  # (f|F|t|T, char) for ; and ,
        self.seek: dict | None = None  # s<char>: None | {"char": None} | {"char": c, "labels": {label: (r, c)}}
        self.trace: list[list] = []  # run-length [token, n] of commands, for the activity log

    def _trace(self, tok: str) -> None:
        if self.trace and self.trace[-1][0] == tok:
            self.trace[-1][1] += 1
        elif len(self.trace) < 5000:
            self.trace.append([tok, 1])

    def take_trace(self) -> list[list]:
        t, self.trace = self.trace, []
        return t

    # -- file -----------------------------------------------------------------
    def open(self, path: Path | None) -> None:
        self.path = path
        if path is None:
            self.lines = [""]
            self.msg = "(no file for this problem)"
        else:
            text = path.read_text().replace("\t", INDENT)
            self.lines = text.split("\n")
            if len(self.lines) > 1 and self.lines[-1] == "":
                self.lines.pop()
            self.msg = f'"{path.name}" {len(self.lines)}L'
        self.row = self.col = self.top = self.left = 0
        self.mode, self.pending, self.cmd = "normal", "", ""
        self.seek = None
        self.undo, self.redo = [], []
        self.dirty = False
        self.refresh()

    def save(self) -> None:
        if self.path is None:
            return
        self.path.write_text("\n".join(self.lines) + "\n")
        self.dirty = False
        self.msg = f'"{self.path.name}" written'
        self.refresh()
        self.post_message(self.Saved())

    def save_if_dirty(self) -> None:
        if self.dirty:
            self.save()

    # -- editing helpers ------------------------------------------------------
    @property
    def line(self) -> str:
        return self.lines[self.row]

    def _set(self, text: str) -> None:
        self.lines[self.row] = text
        self.dirty = True

    def snapshot(self) -> None:
        self.undo.append((list(self.lines), self.row, self.col))
        self.redo.clear()
        if len(self.undo) > 500:
            self.undo.pop(0)

    def _restore(self, src: list, dst: list) -> None:
        if not src:
            self.msg = "nothing to undo" if src is self.undo else "nothing to redo"
            return
        dst.append((list(self.lines), self.row, self.col))
        self.lines, self.row, self.col = src.pop()
        self.dirty = True

    def clamp(self) -> None:
        self.row = max(0, min(self.row, len(self.lines) - 1))
        limit = len(self.line) if self.mode == "insert" else max(len(self.line) - 1, 0)
        self.col = max(0, min(self.col, limit))

    # -- motions: each returns a (row, col) ------------------------------------
    def _next_word(self, r: int, c: int) -> tuple[int, int]:
        line = self.lines[r]
        if c < len(line) and _cls(line[c]):
            k = _cls(line[c])
            while c < len(line) and _cls(line[c]) == k:
                c += 1
        while True:
            line = self.lines[r]
            while c < len(line) and line[c].isspace():
                c += 1
            if c < len(line):
                return r, c
            if r + 1 >= len(self.lines):
                return r, len(line)
            r, c = r + 1, 0
            if self.lines[r] == "":
                return r, 0

    def _word_end(self, r: int, c: int) -> tuple[int, int]:
        c += 1
        while True:
            line = self.lines[r]
            while c < len(line) and line[c].isspace():
                c += 1
            if c < len(line):
                break
            if r + 1 >= len(self.lines):
                return r, max(len(line) - 1, 0)
            r, c = r + 1, 0
        k = _cls(line[c])
        while c + 1 < len(line) and _cls(line[c + 1]) == k:
            c += 1
        return r, c

    def _prev_word(self, r: int, c: int) -> tuple[int, int]:
        c -= 1
        while True:
            line = self.lines[r]
            while c >= 0 and line[c].isspace():
                c -= 1
            if c >= 0:
                break
            if r == 0:
                return 0, 0
            r -= 1
            c = len(self.lines[r]) - 1
            if not self.lines[r]:
                return r, 0
        k = _cls(line[c])
        while c > 0 and _cls(line[c - 1]) == k:
            c -= 1
        return r, c

    def motion(self, m: str, n: int, count_given: bool) -> tuple[int, int] | None:
        r, c = self.row, self.col
        half = max(1, (self.size.height - 1) // 2)
        if m in ("h", "left"):
            return r, max(c - n, 0)
        if m in ("l", "right"):
            return r, c + n
        if m in ("j", "down"):
            return r + n, c
        if m in ("k", "up"):
            return r - n, c
        if m == "ctrl+d":
            return r + half, c
        if m == "ctrl+u":
            return r - half, c
        if m == "0" or m == "home":
            return r, 0
        if m == "^":
            return r, len(_indent(self.line))
        if m == "$" or m == "end":
            return r, len(self.line)
        if m == "gg":
            return (n - 1 if count_given else 0), 0
        if m == "G":
            return (n - 1 if count_given else len(self.lines) - 1), 0
        if (k := self._find_kind(m)) is not None:
            if len(m) == 2:
                self.last_find = (m[0], m[1])
                target, repeat = m[1], False
            else:
                target, repeat = self.last_find[1], True
            col = _find_in_line(self.line, c, k, target, n, repeat)
            return None if col is None else (r, col)
        if m in ("w", "e", "b"):
            fn = {"w": self._next_word, "e": self._word_end, "b": self._prev_word}[m]
            for _ in range(n):
                r, c = fn(r, c)
            return r, c
        return None

    def _find_kind(self, m: str) -> str | None:
        """f/F/t/T for a find motion ("f;", "t)") or a repeat (";" same way, "," reversed)."""
        if len(m) == 2 and m[0] in "fFtT":
            return m[0]
        if m in (";", ",") and self.last_find:
            k = self.last_find[0]
            return k if m == ";" else k.swapcase()
        return None

    # -- key handling -----------------------------------------------------------
    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+g":
            return  # app binding: back to forge
        event.stop()
        event.prevent_default()
        ch = event.character if event.character and event.character.isprintable() else None
        if self.seek is not None:
            self.key_seek(event.key, ch)
        elif self.mode == "insert":
            self.key_insert(event.key, ch)
        elif self.mode == "command":
            self.key_command(event.key, ch)
        else:
            self.msg = ""
            self.key_normal(event.key, ch)
        self.clamp()
        self.scroll_to_cursor()
        self.refresh()

    def on_paste(self, event: events.Paste) -> None:
        event.stop()
        if self.mode != "insert":
            self.snapshot()
            self.mode = "insert"
        for ch in event.text.replace("\r\n", "\n").replace("\t", INDENT):
            if ch == "\n":
                self._split_line(auto_indent=False)
            else:
                self._set(self.line[: self.col] + ch + self.line[self.col :])
                self.col += 1
        self.mode = "normal"
        self.clamp()
        self.scroll_to_cursor()
        self.refresh()

    def key_insert(self, key: str, ch: str | None) -> None:
        line, c = self.line, self.col
        self._trace("i:text" if ch is not None and key not in ("tab",) else f"i:<{key}>")
        if key == "escape":
            self.mode = "normal"
            self.col -= 1
        elif key == "enter":
            self._split_line(auto_indent=True)
        elif key == "backspace":
            if c > 0:
                width = len(INDENT) if line[:c].endswith(INDENT) and not line[:c].strip() else 1
                self._set(line[: c - width] + line[c:])
                self.col -= width
            elif self.row > 0:
                prev = self.lines[self.row - 1]
                del self.lines[self.row]
                self.row -= 1
                self.col = len(prev)
                self._set(prev + line)
        elif key == "delete":
            if c < len(line):
                self._set(line[:c] + line[c + 1 :])
            elif self.row + 1 < len(self.lines):
                self._set(line + self.lines.pop(self.row + 1))
        elif key == "tab":
            self._set(line[:c] + INDENT + line[c:])
            self.col += len(INDENT)
        elif key in ("left", "right", "up", "down", "home", "end"):
            self.row, self.col = self.motion(key, 1, False)
        elif ch is not None:
            if ch == "}" and not line[:c].strip() and c >= len(INDENT):
                line, c = line[: c - len(INDENT)] + line[c:], c - len(INDENT)
            self._set(line[:c] + ch + line[c:])
            self.col = c + 1

    def _split_line(self, auto_indent: bool) -> None:
        line, c = self.line, self.col
        head, tail = line[:c], line[c:]
        indent = _indent(line) if auto_indent else ""
        if auto_indent and head.rstrip().endswith("{"):
            indent += INDENT
        if auto_indent:
            tail = tail.lstrip(" ")
        self._set(head.rstrip() if auto_indent and not head.strip() == "" else head)
        self.lines.insert(self.row + 1, indent + tail)
        self.row += 1
        self.col = len(indent)

    def key_command(self, key: str, ch: str | None) -> None:
        if key == "escape":
            self.mode, self.cmd = "normal", ""
        elif key == "backspace":
            if not self.cmd:
                self.mode = "normal"
            self.cmd = self.cmd[:-1]
        elif key == "enter":
            self.mode = "normal"
            self._trace(":" + self.cmd.strip())
            self.run_command(self.cmd.strip())
            self.cmd = ""
        elif ch is not None:
            self.cmd += ch

    def run_command(self, cmd: str) -> None:
        if cmd in ("w", "wq", "x"):
            self.save()
        if cmd in ("q", "q!", "wq", "x"):
            self.post_message(self.Quit())
        elif cmd.isdigit():
            self.row = int(cmd) - 1
        elif cmd != "w":
            self.msg = f"not a command: {cmd}"

    # -- seek (flash.nvim-style): s<char>, then the label shown after a match ---------
    def key_seek(self, key: str, ch: str | None) -> None:
        seek, self.seek = self.seek, None
        if ch is None:  # escape or any special key cancels
            return
        if seek["char"] is None:
            labels = self._seek_targets(ch)
            if not labels:
                self.msg = f"no {ch!r} on screen"
            elif len(labels) == 1:
                self._seek_jump(ch, "", labels[SEEK_LABELS[0]])
            else:
                self.seek = {"char": ch, "labels": labels}
        elif ch in seek["labels"]:
            self._seek_jump(seek["char"], ch, seek["labels"][ch])

    def _seek_targets(self, ch: str) -> dict[str, tuple[int, int]]:
        """Visible matches of ch (not under the cursor), nearest first, keyed by label."""
        rows = max(self.size.height - 1, 1)
        hi = self.left + max(self.size.width - self.numw, 1)
        hits = []
        for r in range(self.top, min(self.top + rows, len(self.lines))):
            line = self.lines[r]
            c = line.find(ch, self.left)
            while c != -1 and c < hi - 1:  # keep room for the label
                if (r, c) != (self.row, self.col):
                    hits.append((abs(r - self.row), abs(c - self.col), r, c))
                c = line.find(ch, c + 1)
        hits.sort()
        return {lab: (r, c) for lab, (_, _, r, c) in zip(SEEK_LABELS, hits)}

    def _seek_jump(self, ch: str, label: str, pos: tuple[int, int]) -> None:
        self._trace("s" + ch + label)
        self.row, self.col = pos

    def key_normal(self, key: str, ch: str | None) -> None:
        if key == "escape":
            self._trace("<esc>")
            self.pending = ""
            return
        token = ch if ch is not None else key
        if ch is None and key not in ("ctrl+d", "ctrl+u", "ctrl+r", "left", "right", "up", "down",
                                      "home", "end", "enter", "backspace"):
            self.pending = ""
            return
        seq = self.pending + token if ch is not None else token
        m = re.fullmatch(r"([1-9]\d*)?(.*)", seq, re.S)
        count_given = m.group(1) is not None
        n = int(m.group(1) or 1)
        rest = m.group(2)
        if om := re.fullmatch(r"([dyc])([1-9]\d*)(.*)", rest, re.S):  # d2w == 2dw
            if not om.group(3):
                self.pending = seq
                return
            n, count_given, rest = n * int(om.group(2)), True, om.group(1) + om.group(3)
        if (rest in ("", "g", "z", "d", "y", "c", "r", "f", "F", "t", "T")
                or (rest[:1] in "dyc" and rest[1:] in ("g", "a", "i", "f", "F", "t", "T"))):
            self.pending = seq
            return
        self.pending = ""
        if rest == "s":  # seek; a count is ignored
            self.seek = {"char": None}
            return
        if rest != ":":  # the full ":cmd" is traced on enter
            self._trace(seq if ch is not None else f"<{token}>")
        self.execute(rest, n, count_given)

    def execute(self, op: str, n: int, count_given: bool) -> None:
        if op == "enter":
            op = "j"
        if op == "backspace":
            op = "h"
        pos = self.motion(op, n, count_given)
        if pos is not None:
            self.row, self.col = pos
            if op in ("j", "k", "down", "up", "ctrl+d", "ctrl+u"):
                self.clamp()
            if op in ("gg", "G"):
                self.row = max(0, min(self.row, len(self.lines) - 1))
                self.col = len(_indent(self.line))
            if op in ("$", "end"):
                self.col = max(len(self.line) - 1, 0)
            return

        if op in ("zz", "zt", "zb"):  # put the cursor line at the center / top / bottom
            if count_given:
                self.row = max(0, min(n - 1, len(self.lines) - 1))
            rows = max(self.size.height - 1, 1)
            off = {"zz": rows // 2, "zt": 0, "zb": rows - 1}[op]
            self.top = max(0, self.row - off)
            return
        if op == ":":
            self.mode, self.cmd = "command", ""
            return
        if op == "u":
            self._restore(self.undo, self.redo)
            return
        if op == "ctrl+r":
            self._restore(self.redo, self.undo)
            return

        if op in ("i", "a", "I", "A", "o", "O"):
            self.snapshot()
            self.mode = "insert"
            if op == "a" and self.line:
                self.col += 1
            elif op == "I":
                self.col = len(_indent(self.line))
            elif op == "A":
                self.col = len(self.line)
            elif op in ("o", "O"):
                # like pressing enter at the end of the line above the new one
                above = self.line if op == "o" else (self.lines[self.row - 1] if self.row else "")
                indent = _indent(above) + (INDENT if above.rstrip().endswith("{") else "")
                at = self.row + 1 if op == "o" else self.row
                self.lines.insert(at, indent)
                self.row, self.col = at, len(indent)
                self.dirty = True
            return

        if op == "p" or op == "P":
            text, linewise = self.reg
            if not text:
                return
            self.snapshot()
            if linewise:
                at = self.row + 1 if op == "p" else self.row
                self.lines[at:at] = text * n
                self.row, self.col = at, len(_indent(text[0]))
            else:
                t, o = self._flat()
                at = o + 1 if op == "p" and self.line else o
                s = "\n".join(text) * n
                self._set_flat(t[:at] + s + t[at:], at + max(len(s) - 1, 0))
            self.dirty = True
            return

        if len(op) == 2 and op[0] == "r":
            if self.col < len(self.line):
                self.snapshot()
                self._set(self.line[: self.col] + op[1] + self.line[self.col + 1 :])
            return

        if op in ("x", "X"):
            if not self.line or (op == "X" and self.col == 0):
                return
            self.snapshot()
            a, b = (self.col, self.col + n) if op == "x" else (max(self.col - n, 0), self.col)
            self.reg = ([self.line[a:b]], False)
            self._set(self.line[:a] + self.line[b:])
            self.col = a
            return

        if op == "J":
            if self.row + 1 < len(self.lines):
                self.snapshot()
                nxt = self.lines.pop(self.row + 1).lstrip()
                self.col = len(self.line)
                self._set(self.line.rstrip() + (" " + nxt if nxt else ""))
            return

        if op in ("D", "C"):
            op = op.lower() + "$"

        if op in ("dd", "yy", "cc"):
            last = min(self.row + n, len(self.lines))
            self.reg = (self.lines[self.row : last], True)
            if op == "yy":
                self.msg = f"{last - self.row} line(s) yanked"
                return
            self.snapshot()
            if op == "dd":
                del self.lines[self.row : last]
                if not self.lines:
                    self.lines = [""]
                self.row = min(self.row, len(self.lines) - 1)
                self.col = len(_indent(self.line))
            else:
                indent = _indent(self.line)
                del self.lines[self.row + 1 : last]
                self.lines[self.row] = indent
                self.col = len(indent)
                self.mode = "insert"
            self.dirty = True
            return

        if len(op) == 3 and op[0] in "dyc" and op[1] in "ai":
            self._textobj_op(op[0], op[1], op[2])
            return

        if len(op) >= 2 and op[0] in "dyc":
            verb, m = op[0], op[1:]
            if verb == "c" and m == "w":
                m = "e"  # vim: cw acts like ce
            pos = self.motion(m, n, count_given)
            if pos is None or m in ("j", "k", "gg", "G"):
                return
            r, tc = pos
            if r != self.row:
                tc = len(self.line) if r > self.row else 0
            elif m == "e" or self._find_kind(m) in ("f", "t"):
                tc += 1  # inclusive motions
            a, b = sorted((self.col, tc))
            b = min(b, len(self.line))
            self.reg = ([self.line[a:b]], False)
            if verb == "y":
                return
            self.snapshot()
            self._set(self.line[:a] + self.line[b:])
            self.col = a
            if verb == "c":
                self.mode = "insert"

    # -- text objects (da( ci{ yi" daw ...) --------------------------------------------
    def _flat(self) -> tuple[str, int]:
        """The buffer as one string, and the cursor as an offset into it."""
        return "\n".join(self.lines), sum(len(l) + 1 for l in self.lines[: self.row]) + self.col

    def _set_flat(self, text: str, offset: int) -> None:
        self.lines = text.split("\n")
        before = text[:offset]
        self.row = before.count("\n")
        self.col = offset - (before.rfind("\n") + 1)
        self.dirty = True

    def _textobj_op(self, verb: str, kind: str, obj: str) -> None:
        t, o = self._flat()
        rng = self._textobj(t, o, kind, obj)
        if rng is None:
            return
        a, b = rng
        if b > a and t[b - 1] == "\n" and (a == 0 or t[a - 1] == "\n"):
            self.reg = (t[a : b - 1].split("\n"), True)  # whole lines (di{ on a block): linewise
        else:
            self.reg = (t[a:b].split("\n"), False)
        if verb == "y":
            self._set_flat(t, a)
            return
        self.snapshot()
        new, cur = t[:a] + t[b:], a
        if verb == "c" and kind == "i" and obj in BRACKETS and t[a:b].endswith("\n"):
            # ci{ on a multi-line block: leave one indented empty line to type on
            line_start = t.rfind("\n", 0, a - 1) + 1  # the line holding the "{"
            indent = _indent(t[line_start:]) + INDENT
            new, cur = new[:a] + indent + "\n" + new[a:], a + len(indent)
        self._set_flat(new, cur)
        if verb == "c":
            self.mode = "insert"

    def _textobj(self, t: str, o: int, kind: str, obj: str) -> tuple[int, int] | None:
        if obj in BRACKETS:
            return _bracket_obj(t, o, kind, *BRACKETS[obj])
        if obj in "\"'`":
            ls = t.rfind("\n", 0, o) + 1
            le = t.find("\n", o)
            le = len(t) if le < 0 else le
            r = _quote_obj(t[ls:le], o - ls, kind, obj)
            return None if r is None else (r[0] + ls, r[1] + ls)
        if obj in "wW":
            return _word_obj(t, o, kind, big=obj == "W")
        return None

    # -- rendering ------------------------------------------------------------------
    @property
    def numw(self) -> int:
        return len(str(len(self.lines))) + 2

    def scroll_to_cursor(self) -> None:
        rows = max(self.size.height - 1, 1)
        cols = max(self.size.width - self.numw - 1, 1)
        if self.row < self.top:
            self.top = self.row
        elif self.row >= self.top + rows:
            self.top = self.row - rows + 1
        if self.col < self.left:
            self.left = self.col
        elif self.col >= self.left + cols:
            self.left = self.col - cols + 1

    def on_resize(self, _event) -> None:
        self.scroll_to_cursor()

    def on_focus(self) -> None:
        self.refresh()

    def on_blur(self) -> None:
        self.refresh()

    def render_line(self, y: int) -> Strip:
        width = self.size.width
        if y == self.size.height - 1:
            return self._status(width)
        idx = self.top + y
        if idx >= len(self.lines):
            return Strip([Segment("~", NUM)]).adjust_cell_length(width)
        g = self.numw
        line = self.lines[idx]
        styles = highlight(line, self.comment_state(idx))[0] if self.syntax else [None] * len(line)
        lo, hi = self.left, self.left + width - g
        text, styles = line[lo:hi], styles[lo:hi]
        labels = {}
        if self.seek and self.seek.get("labels"):
            labels = {c + 1 - lo: lab for lab, (r, c) in self.seek["labels"].items() if r == idx}
            if labels and max(labels) >= len(text):
                n = min(max(labels) + 1, hi - lo)
                text, styles = text.ljust(n), styles + [None] * (n - len(text))
            text = "".join(labels.get(i, t) for i, t in enumerate(text))
            styles = [LABEL if i in labels else st for i, st in enumerate(styles)]
        cur = self.col - self.left if idx == self.row and self.has_focus and self.mode != "command" else -1
        if cur >= len(text):
            text, styles = text.ljust(cur + 1), styles + [None] * (cur + 1 - len(text))
        segs = [Segment(f"{idx + 1:>{g - 1}} ", NUM)]
        run, run_style = "", None
        for i, ch in enumerate(text):
            st = CURSOR if i == cur else styles[i]
            if st is not run_style and run:
                segs.append(Segment(run, run_style))
                run = ""
            run, run_style = run + ch, st
        if run:
            segs.append(Segment(run, run_style))
        return Strip(segs).adjust_cell_length(width)

    @property
    def syntax(self) -> bool:
        return self.path is not None and self.path.suffix in (".c", ".h")

    def comment_state(self, idx: int) -> bool:
        """Is a /* comment open at the start of line idx? Recomputed when the text changes."""
        key = tuple(self.lines)
        if getattr(self, "_cs_key", None) != key:
            state, out = False, []
            for ln in self.lines:
                out.append(state)
                state = highlight(ln, state)[1]
            self._cs_key, self._cs = key, out
        return self._cs[idx]

    def _status(self, width: int) -> Strip:
        if self.mode == "command":
            return Strip([Segment(":" + self.cmd), Segment(" ", CURSOR)]).adjust_cell_length(width)
        left = "-- INSERT -- " if self.mode == "insert" else ""
        left += self.msg or self.pending or ("s" if self.seek is not None else "")
        name = (self.path.name if self.path else "[no file]") + (" [+]" if self.dirty else "")
        right = f"{name}  {self.row + 1}:{self.col + 1} "
        pad = max(width - len(left) - len(right), 1)
        return Strip([Segment(left), Segment(" " * pad), Segment(right, STATUS)]).adjust_cell_length(width)


BRACKETS = {"(": "()", ")": "()", "b": "()", "{": "{}", "}": "{}", "B": "{}",
            "[": "[]", "]": "[]", "<": "<>", ">": "<>"}


def _bracket_obj(t: str, o: int, kind: str, op: str, cl: str) -> tuple[int, int] | None:
    """The innermost op...cl pair around offset o (vim's i( / a( and friends)."""
    if o < len(t) and t[o] == cl:
        o -= 1  # on the closing bracket: it belongs to the pair we're in
    depth, start = 0, None
    for i in range(min(o, len(t) - 1), -1, -1):
        if t[i] == cl:
            depth += 1
        elif t[i] == op:
            if depth == 0:
                start = i
                break
            depth -= 1
    if start is None:
        return None
    depth = 0
    for j in range(start + 1, len(t)):
        if t[j] == op:
            depth += 1
        elif t[j] == cl:
            if depth == 0:
                break
            depth -= 1
    else:
        return None
    if kind == "a":
        return start, j + 1
    a, b = start + 1, j
    if t[a:b].startswith("\n"):  # multi-line block: keep the bracket lines themselves
        a += 1
        last_nl = t.rfind("\n", a - 1, b)
        if last_nl >= a - 1 and not t[last_nl + 1 : b].strip():
            b = last_nl + 1
        a = min(a, b)
    return a, b


def _quote_obj(line: str, c: int, kind: str, q: str) -> tuple[int, int] | None:
    idx, i = [], 0
    while i < len(line):
        if line[i] == "\\":
            i += 2
            continue
        if line[i] == q:
            idx.append(i)
        i += 1
    pairs = list(zip(idx[::2], idx[1::2]))
    pick = next((p for p in pairs if p[0] <= c <= p[1]), None) or next((p for p in pairs if p[0] > c), None)
    if pick is None:
        return None
    s, e = pick
    if kind == "i":
        return s + 1, e
    e += 1
    while e < len(line) and line[e] == " ":
        e += 1
    return s, e


def _word_obj(t: str, o: int, kind: str, big: bool) -> tuple[int, int] | None:
    if not t:
        return None
    o = min(o, len(t) - 1)

    def cls(ch: str) -> int:
        if ch.isspace():
            return 0
        return 1 if big or ch.isalnum() or ch == "_" else 2

    k = cls(t[o])
    a = o
    while a > 0 and t[a - 1] != "\n" and cls(t[a - 1]) == k:
        a -= 1
    b = o
    while b < len(t) and t[b] != "\n" and cls(t[b]) == k:
        b += 1
    if kind == "a" and k != 0:
        e = b
        while e < len(t) and t[e] in " \t":
            e += 1
        if e > b:
            b = e
        else:
            while a > 0 and t[a - 1] in " \t":
                a -= 1
    return a, b


def _find_in_line(line: str, c: int, kind: str, ch: str, n: int, repeat: bool) -> int | None:
    """Column the cursor lands on for vim's f/F/t/T (n-th occurrence), or None if not found."""
    fwd = kind in "ft"
    i = c
    if repeat and kind in "tT":
        i += 1 if fwd else -1  # ; after t: don't get stuck right before the same char
    for _ in range(n):
        i = line.find(ch, i + 1) if fwd else line.rfind(ch, 0, max(i, 0))
        if i < 0:
            return None
    if kind == "t":
        return i - 1
    if kind == "T":
        return i + 1
    return i
