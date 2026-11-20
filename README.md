# forge

Learn big things by building them, in small hands-on steps, without leaving the terminal.
First course: **Build a C Compiler in C** (arm64 macOS) for **mini-C**, a small C subset ([spec](courses/c-compiler/LANGUAGE.md)). Design: [DESIGN.md](DESIGN.md).

## Run

```sh
uv run forge                 # TUI: problem + built-in vim + tests (tree is a drawer on small screens)
uv run forge list            # course tree with progress
uv run forge open 0.1-03     # CLI flow: open → edit → run → submit
uv run forge run | submit | hint | answer <n|text> | solution | reset
uv run forge check [prefix]  # authoring: ref solutions pass, starters fail
```

Your code lives in `~/forge-work/<course>/drills/<id>/`. Progress is in `~/.local/share/forge/<course>.json`. Override with `FORGE_WORK`,
`FORGE_DATA`, `FORGE_COURSES`.

Activity log (local only, for coaching): `~/.local/share/forge/<course>.activity.jsonl`. It records opens, runs and submits
with code snapshots and results, answers, hints, lessons, and a run-length trace of vim commands. Set `FORGE_NO_ACTIVITY=1` to
turn it off.

## TUI keys

All forge actions are on ctrl and work everywhere, including inside vim:

| key | action |
|---|---|
| `^g` | editor ⇄ forge (`enter` also opens the editor, `:q` leaves it) |
| `^e` / `^s` | run example tests / submit (all tests). `:w` also runs the example tests |
| `^n` / `^p` | next / prev problem |
| `^l` | toggle lesson |
| `^t` / `^q` | show / hide course tree / quit |
| `^f` | focus mode: hide the problem text, editor only (a hint or `^l` brings it back) |
| outside the editor | `h` next hint (costs a star), `1`–`9` answer a quiz, `j`/`k`/`space` scroll the text, arrows+`enter` in the tree |
| `S` / `R` (outside the editor) | show solution (→ 0 stars) / reset starter code |

Screen adapts to its size: ≥130 cols shows the tree; with <110 cols left the problem text
stacks above the editor; quiz/predict problems hide the editor and test panel.

Stars: ★★★ unaided, −1 per hint, −1 per wrong quiz answer (min ★), 0 if you viewed the solution.

## Layout

```
src/forge/          engine (Python, Textual)
  course.py         content model, loaded from courses/<id>/chapters/...
  runner.py         compile + run C tests (ASan+UBSan), quiz/predict grading
  session.py        actions shared by CLI and TUI; progress.py, workspace.py
  check.py          `forge check`
  tui/app.py        the app; tui/vim.py = small built-in vim with C highlighting
courses/c-compiler/
  harness/          forge_test.h/.c: forked-per-test C harness, JSON-line results
  chapters/00-c-refresher/{01-pointers,02-strings,03-dynamic-arrays,04-arena}/
```

Problem format: see DESIGN.md §5 or any directory under `courses/c-compiler/chapters/`.

## Built-in vim

Deliberately small; no plugins, no config. C/H files get regex syntax highlighting.

- normal: `h j k l w b e 0 ^ $ gg G ctrl+d ctrl+u zz zt zb`, `f F t T` + `;` `,`, counts (`3j`, `2dd`, `5G`, `d2w`)
- edit: `i a I A o O x X r<c> J dd cc yy D C p P u ctrl+r`, operators `d c y` + `w e b 0 $ f F t T ; ,` (e.g. `ct;`, `df)`)
- text objects: `d c y` + `i`/`a` + `( ) b`, `{ } B`, `[ ]`, `< >` (multi-line), `"` `'` ``` ` ```, `w W` (e.g. `da(`, `ci{`, `yi"`, `daw`)
- seek (flash.nvim-style): `s` + char labels every visible match (nearest first) with a letter right after it; type the letter to jump, `Esc` cancels. One match jumps at once. (Replaces vim's `s` = substitute.)
- insert: auto-indent (extra level after `{`, `}` dedents), tab = 4 spaces, backspace removes an indent level
- command: `:w` (also runs tests) `:q` `:wq` `:x` `:<line>`
- switching problems saves the current buffer

Not supported: visual mode, search, `.` repeat, macros, multiple buffers.

## Project mode (chapter 1+)

From chapter 1, code problems with `mode = "project"` all edit one program, your compiler, in
`~/forge-work/c-compiler/project/` (created from `courses/c-compiler/scaffold/` on first open):

```
cd ~/forge-work/c-compiler/project
make                  # builds ./mcc (warnings are errors)
make try P=prog.c     # compile prog.c with your mcc, run it, print the exit code
./mcc prog.c -o -     # show the assembly your compiler emits
```

Tests are unit tests (linked against every `src/*.c` except `main.c`) and/or `[[e2e]]` cases: forge builds
`mcc`, compiles each case's mini-C source, assembles + links with `cc`, runs it and compares the exit code /
stdout. Failures show the source and *your generated assembly*. `R` (reset) in project mode keeps the old
file as `<file>.bak`, since one file can hold several problems' work.

## Not built yet

- Checkpoints / `forge adopt` (skip ahead with reference code), git commit per submit, chapter locks, review queue.
