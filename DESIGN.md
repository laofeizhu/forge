# forge — learn by building, in the terminal

Status: prototype built (2026-11-04): engine, TUI with built-in vim, chapter 0 (17 problems). See README.md.

## 1. Goal

A terminal app for learning big engineering topics (first course: **build a C compiler in C**) through
many small, hands-on problems. Two inspirations:

| From **LeetCode** | From **Beast Academy** |
|---|---|
| Problem statement, examples, constraints | Short "guide" lesson *before* practice, concrete before abstract |
| Visible example tests + hidden tests on submit | Problems ramp in tiny steps; puzzles, not just exercises |
| Instant pass/fail with diffs | Hints that nudge, not solve; stars for solving unaided |
| You write real code in a real editor | Optional starred "challenge" problems for depth |

Design principles:

1. **Write real code, in vim keys, without leaving forge.** A small built-in vim; `:w` runs the tests.
2. **Small steps, fast feedback.** Every problem should take 5–30 minutes; tests run in < 2 s on save.
3. **The project grows.** Drills are standalone, but most problems add a piece to *your* compiler.
4. **Never get stuck.** Hints are graded; the reference solution is always one key away.
5. **Engine and content are separate.** A course is a folder of Markdown + TOML + test files. Any topic
   (compiler, OS kernel, database, networking) is just another course.

## 2. Core concepts

```
Course   → c-compiler
 Chapter → 03 · Parsing expressions
  Part   → 03.2 · Precedence climbing        (one lesson + a handful of problems)
   Lesson   lesson.md   — the "guide": 1–3 screens, worked examples, ASCII diagrams
   Problem  01-warmup   — quiz: "which tree does 1 + 2 * 3 parse to?"
   Problem  02-drill    — code: implement parse_primary()
   Problem  03-build    — code: wire binary ops into your compiler (project)
   Problem  04-challenge★ — optional: right-associative `=` and `?:`
```

### Problem kinds

| Kind | What you do | How it's checked |
|---|---|---|
| `quiz` | Multiple choice / short answer inside the TUI | Compare to answer key (normalized) |
| `predict` | Read code, predict output / tokens / AST / asm | Compare to expected text |
| `code` (drill) | Implement a function in a standalone file | C unit tests linked against your file |
| `code` (project) | Implement/extend a file in your growing compiler | Unit tests **and** end-to-end programs |
| `fix` | A buggy snippet is given; make the tests pass | Same as `code` |

`quiz`/`predict` are the Beast Academy "puzzle" layer: cheap, fast checks of understanding before writing code.

## 3. User experience

### Layout (TUI)

```
┌ forge · c-compiler ────────────────────────────────────── ★ 41  🔥 6 days ┐
│ ▾ 02 Lexer          ✓  │ 03.2-02 · parse_primary()            easy · code │
│ ▾ 03 Parsing        ◐  │                                                  │
│   ✓ 03.1 Grammars      │ Implement `Node *parse_primary(Parser *p)` that  │
│   ▸ 03.2 Precedence    │ parses an integer literal or a parenthesized     │
│     ✓ 01 warmup  ★★★   │ expression.                                      │
│     ▸ 02 drill         │                                                  │
│     · 03 build         │ Example 1                                        │
│     · 04 challenge ★   │   input:  "42"                                   │
│ ▸ 04 Codegen        🔒 │   output: NUM(42)                                │
│                        │ Example 2                                        │
│                        │   input:  "(1)"                                  │
│                        │   output: NUM(1)                                 │
│                        │                                                  │
│                        │ Constraints: no heap allocation outside arena.   │
├────────────────────────┴──────────────────────────────────────────────────┤
│ Tests  ✓ example_1  ✗ example_2   expected NUM(1)  got  <error: ')' >     │
│ watching src/parse.c · last run 0.4s · ASan+UBSan on                      │
└ r run · s submit · h hint (1/3) · e edit · l lesson · ? help ─────────────┘
```

### Built-in editor (vim)

Responsive layout (`_relayout` in `tui/app.py`, driven by screen resize): wide (≥130 cols) is
tree | problem | editor with tests underneath; narrower, the tree becomes a drawer (`^t`, closes on
pick) and when <110 cols remain the problem text (45% height) stacks above the editor; quiz/predict
problems drop the editor and test panel and show the result inline. `Ctrl-g`/`Enter` move focus
to the editor; `:q`/`Esc` return to forge.

- **What it is**: a small vim written for forge (`tui/vim.py`, ~550 lines): one buffer, normal /
  insert / command modes, the common motions and operators with counts, undo/redo, C-aware
  auto-indent, and cheap regex syntax highlighting for `.c`/`.h`.
- **Integration is direct**: `:w` saves and re-runs the visible tests; switching problems saves and
  opens the next file. No subprocess, socket, or terminal emulation.
- **Why not embed Neovim?** The first prototype did (PTY + pyte). It worked, but brought a terminal
  emulator, an RPC socket, tty-mode bugs and escape-key ambiguity. A small purpose-built vim is less
  code and fully under forge's control. Missing features (visual mode, search, `.`) can be added as needed.

### CLI (works without the TUI too)

```
forge                       # open TUI at where you left off
forge list                  # course tree with status
forge open 03.2-02          # jump to a problem
forge run | submit          # visible tests / all tests (records result)
forge answer <n|text>       # quiz / predict
forge hint | solution       # next hint / reference (marks problem "assisted")
forge reset                 # restore starter code
forge check [prefix]        # authoring: validate a course (see §6)
```

### Progress & motivation (Beast Academy flavor)

- **Stars per problem**: ★★★ unaided, −1 per hint and per wrong quiz answer (min ★), 0 if the solution was viewed.
- **Locks**: a chapter unlocks when the previous chapter's non-challenge problems are done
  (configurable; `--free` mode unlocks everything).
- **Streak / daily goal** in the header; keep it subtle.
- **Review queue**: wrong quiz answers come back after 1, 3, 7 days.

## 3b. Learner profile and how the course adapts (from chapter 0's activity log)

The course is written for one learner (Kupatupa); this is what chapter 0 showed and what follows from it.

| observed | course response |
|---|---|
| strong on pointers/strings, solves without hints, persistent | fewer drills, more project work; ★ problems in every chapter |
| things click through **hand-traced memory/state diagrams** ("brain simulation") and `fprintf(stderr)` | every lesson draws state (bytes, registers, cursor offsets) as tables; each part opens with a `predict` trace of exactly the mechanism its code problem uses; the compiler gets dump modes (`--tokens`, `--ast`) as debug output, not a debugger |
| bugs cluster on **library contracts** (`realloc(NULL)`, `free` doesn't NULL, `strncpy`, `va_list`) and **ownership / pass-by-value** (`free(p)`, `a =` vs `*a =`) | a short "Contract:" box whenever a lesson leans on a libc function; ownership called out explicitly ("who frees what") in the driver and every API |
| bugs cluster on **when state changes** (grow conditions, zero at alloc vs init) | trace tables include the edge states: empty `{0}`, exactly full, after reset |
| submit used as an oracle (11 submits, 6× same score), runs 20-40 s apart, warnings ignored (one *was* the bug) | each code README ends with **"Trace these before you submit"**, the hidden cases spelled out as inputs; `-Werror` from chapter 1 (`werror = true` in chapter.toml); after 2+ failed submits forge prints a nudge to trace a failing test |
| prefers minimal tools and hands-on play | the project has a 6-line Makefile with `make try P=prog.c` and `./mcc f.c -o -`, so experimenting outside forge is one command |

Pace target: parts of 3-4 problems, each code problem ≤ ~40 lines of new code.

## 4. The project model (the important part)

**Implemented (chapter 1):** `mode = "project"` problems share `~/forge-work/<course>/project/`, created from
`courses/<course>/scaffold/`. A file a problem edits that doesn't exist yet comes from that problem's
`starter/` (or the scaffold). Unit tests link all `src/*.c` except `src/main.c`; `[[e2e]]` cases build the whole
compiler. `forge check` validates problem *k* against scaffold + reference solutions of all project problems
before *k* (starter must fail) and up to *k* (solution must pass). Not yet: git commits, checkpoints/`adopt`.

A compiler course is cumulative: chapter 5 needs a working lexer from chapter 2. Pure LeetCode-style
isolation would never produce a compiler; pure project-style would have big unclear steps. forge does both:

- **Workspace**: `~/forge-work/c-compiler/` is *your* compiler, a real git repo with a `Makefile`.
  forge creates it from the course's `scaffold/` and commits after every passing submit
  (`forge: pass 03.2-03`), so history doubles as a learning journal.
- **Drills** live in `~/forge-work/c-compiler/drills/<id>/` and never touch the project.
- **Project problems** name the file + symbols they own, e.g. `src/parse.c: parse_primary, parse_binary`.
  Tests link the project with a test harness and call those functions directly.
- **Checkpoints**: each chapter ships a reference snapshot. If your project is broken or you skipped ahead,
  `forge adopt --chapter 04` replaces the owned files with the reference so you can continue.
  Your version is kept on a git branch.
- **Interfaces are fixed by the course** (headers in `scaffold/include/`), so tests stay stable while
  implementations vary.

## 5. Content format

A course is a directory (its own git repo, e.g. `~/forge-courses/c-compiler`):

```
c-compiler/
  course.toml
  scaffold/                    # initial workspace: Makefile, include/*.h, src/*.c stubs
  harness/forge_test.h         # tiny header-only C test lib (ASSERT_EQ_INT, ASSERT_EQ_STR, ...)
  chapters/
    03-parsing/
      chapter.toml
      02-precedence/
        lesson.md
        problems/
          01-warmup/problem.toml        # quiz: everything inline
          02-drill/
            problem.toml
            README.md                   # description, examples, constraints
            starter/parse_primary.c
            tests/visible.c             # example tests (shown, run on save)
            tests/hidden.c              # run on submit
            hints.md                    # "---"-separated, increasingly specific
            solution/parse_primary.c
          03-build/ ...
  checkpoints/ch03/src/*.c      # reference project after chapter 3
```

### `problem.toml` — code problem

```toml
id = "03.2-02"
title = "parse_primary()"
kind = "code"            # quiz | predict | code | fix
mode = "drill"           # drill | project
difficulty = "easy"      # easy | medium | hard
challenge = false        # true = optional ★ problem
est_minutes = 15

[files]
edit = ["parse_primary.c"]          # project mode: ["src/parse.c"]
owns = ["parse_primary"]            # symbols this problem defines (for adopt/checkpoints)

[build]
# {edit}, {harness}, {tests} are substituted by forge
cmd = "cc -std=c11 -g -Wall -Wextra -Werror -fsanitize=address,undefined {edit} {tests} -I{harness} -o {out}"

[run]
timeout_s = 2
```

### `problem.toml` — end-to-end compiler tests

Compiler problems also need "compile this C program with *your* compiler, run it, check the result".
That's a second test type, declared as cases instead of C code:

```toml
[[e2e]]
name = "return_42"
source = "int main(void) { return 42; }"
exit_code = 42

[[e2e]]
name = "precedence"
source = "int main(void) { return 2 + 3 * 4; }"
exit_code = 14
hidden = true

[[e2e]]
name = "rejects_missing_semicolon"
source = "int main(void) { return 1 }"
expect_compile_error = true
```

forge runs: `your_cc in.c -o out.s` → `cc out.s -o out` → `./out`, compares exit code / stdout.

### `problem.toml` — quiz / predict

```toml
id = "03.2-01"
title = "Which tree?"
kind = "quiz"
prompt = """
With `*` binding tighter than `+`, which tree does `1 + 2 * 3` parse to?
"""
choices = ["(+ 1 (* 2 3))", "(* (+ 1 2) 3)", "(+ (* 1 2) 3)"]
answer = 0
explain = "`*` has higher precedence, so `2 * 3` groups first and becomes the right operand of `+`."
```

Markdown in `lesson.md` / `README.md` is rendered in the TUI; ASCII diagrams and fenced code are first-class.

## 6. Engine architecture

**Stack: Python + Textual, managed with uv.** Fast to build, great Markdown/Tree widgets, and the
heavy lifting (compiling, running) is subprocesses anyway. (Alternative: Go + Bubble Tea for a single
binary — worth it only if distribution matters.)

```
forge/
  pyproject.toml
  src/forge/
    cli.py          # typer entrypoint: list/open/run/submit/hint/...
    tui/            # Textual app: sidebar tree, problem view, test panel
    course.py       # load + validate course dirs → Course/Chapter/Part/Problem models
    workspace.py    # create workspace from scaffold, place starters, git commits, adopt/checkpoints
    runner/
      base.py       # Runner interface: run(problem, visible_only) -> TestReport
      ctest.py      # build + run C unit tests, parse harness output
      e2e.py        # compile-with-your-compiler → assemble → run → compare
      quiz.py       # answer checking
    watch.py        # watchfiles: re-run visible tests on save (works for any editor)
    tui/vim.py      # built-in vim widget
    progress.py     # SQLite at ~/.local/share/forge/progress.db
```

Key decisions:

- **Test protocol**: `forge_test.h` prints one JSON line per test (`{"name":..,"ok":..,"expected":..,"got":..}`).
  The runner parses it; a crash (ASan report, segfault, timeout) is captured and shown as its own result.
  This keeps the runner language-agnostic: any future course (Rust, Zig, Python) just needs a harness that
  emits the same lines.
- **Sanitizers on by default** (ASan + UBSan). For learning C this is the single biggest win:
  memory bugs show up as clear errors instead of mysterious wrong answers.
- **Isolation**: each run in a temp build dir, wall-clock timeout, `ulimit` on memory/CPU.
  (No container — it's your own code on your own machine.)
- **Progress DB**: problems (status, stars, attempts, time spent, hints used), quiz review schedule.
  Content stays read-only; all user state is in the workspace + DB.
- **`forge course check`** (authoring/CI): for every problem, build the reference solution and assert all
  tests pass; build the starter and assert at least one test fails; validate TOML schema and IDs; check that
  each checkpoint passes all tests up to its chapter. This matters a lot if Claude helps generate courses.

## 7. First course: C compiler (sketch)

Source language: **mini-C**, a deliberately small subset of C specified in
[`courses/c-compiler/LANGUAGE.md`](courses/c-compiler/LANGUAGE.md): decimal-only integer literals, 64-bit
`int` as the only scalar type, pointers/arrays (local + global), `if/while/for`, functions with ≤8 args,
`putchar`/`getchar` for I/O, Turing complete (ch 10 capstone: a Brainfuck interpreter written in mini-C),
no preprocessor/strings/structs. Every mini-C program is valid C, so `clang` is a reference oracle for tests.
Cut features come back as optional ★ extensions. Chapter 0 practises *real* C (the language you write the
compiler in); only the compiler's input is mini-C.

Target: **arm64 macOS assembly** (native on this Mac; symbols need a `_` prefix).
Approach is incremental, in the spirit of Ghuloum's "incremental approach" / Sandler's *Writing a C Compiler*:
every chapter ends with a compiler that works end-to-end for a bigger slice of mini-C.

| # | Chapter | You end up with |
|---|---|---|
| 0 | C refresher: pointers, strings, structs, `malloc`, arena allocator, dynamic arrays | utility lib your compiler uses |
| 1 | Big picture: source → tokens → AST → asm; reading arm64 asm, calling `cc` | `return 42` compiler (hard-coded) |
| 2 | Lexer: mini-C tokens, keywords, decimal literals, `//` comments, error locations | `lex()` + token dump |
| 3 | Parsing expressions: grammars, recursive descent, precedence climbing, AST | `parse_expr()` + AST printer |
| 4 | Codegen I: stack machine on arm64, `+ - * / %`, unary `-` | `int main(){return 2+3*4;}` |
| 5 | Comparisons & logic: `== != < <= > >= ! && \|\|`, short-circuit | boolean expressions |
| 6 | Locals & statements: `int x = e;`, assignment, stack frames, blocks, scopes | multi-statement programs |
| 7 | Control flow: `if/else`, `while`, `for`, `break/continue` | loops |
| 8 | Functions: AAPCS64, ≤8 args, recursion, declarations, calling `putchar`; `print_int` in mini-C | `fib(10)` printed |
| 9 | Pointers & arrays: `&`, `*`, scaled pointer arithmetic, `int a[N]`, `a[i]` | sorting an array |
| 10 | Globals & global arrays, `getchar`, semantic checks, good errors; **capstone: Brainfuck interpreter in mini-C** | proof it's Turing complete |
| 11★ | Extensions, pick any: hex/octal, `++`/`+=`, `?:`, bitwise, `char`/strings, structs, IR + folding, regalloc | your own language |

Each part follows the same rhythm: **lesson → predict trace (the exact mechanism) → project build → optional
challenge**, with "Trace these before you submit" on every code problem (see §3b).

Chapter 1 as built: 1.1 the pipeline (stage quiz, count tokens, exit code & 255) · 1.2 reading arm64
(register traces incl. "copy, not link", `_main`, hand-compile `(4+3)*6` as a `.s` file checked by e2e) ·
1.3 first compiler (cursor trace, `emit_program`, `next_token` (a tiny lexer returning slices), `compile()`
checking the token sequence of `int main() { return N; }`,
★ `movz`/`movk` for 64-bit literals with overflow checks).

## 8. Build plan

1. **MVP (CLI only)**: course loader, `code` drill runner with `forge_test.h`, `list/open/run/submit/hint`,
   progress DB. Author chapter 0 by hand to prove the format.
2. **TUI + editor**: sidebar + Markdown view + test panel + built-in vim.
3. **Project mode**: workspace scaffold, owned files, e2e runner, git commits, `adopt` + checkpoints.
4. **Authoring tools**: `forge course check`, `forge new problem` template. Generate chapters 1–4 with Claude,
   validated by `check`.
5. **Polish**: quiz/predict kinds, stars, review queue, streaks.
6. **Later / optional**: AI tutor (`forge ask` sends problem + your code + failing test to Claude for a
   Socratic hint, never a full solution), more courses.

## 9. Open questions

- Target arch: arm64 macOS only, or also x86-64 Linux (via Docker) for portability with most references?
- Should project problems be strictly linear, or allow skipping with auto-adopt of prior checkpoints?
- Course content: hand-written, Claude-generated + reviewed, or adapted from an existing book's structure?
- One repo (engine + courses) to start, split later? (Recommendation: one repo, `courses/` subdir, split once
  the format stabilizes.)
