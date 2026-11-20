# mini-C

The language you build a compiler for in this course: a deliberately small subset of C, sized so that each
feature is a short chapter and the whole compiler stays a few thousand lines you fully understand.

**Rule of thumb:** every mini-C program is also a valid C program. If its values stay within 32-bit range,
`clang` gives the same result, so real C is always available as a reference. Anything not listed here is
**not** mini-C. Your compiler should reject it with an error rather than guess.

The chapter column says when a feature arrives. The language grows with your compiler.

## Lexical

| | mini-C | dropped from C |
|---|---|---|
| integers | decimal only: `0` or `[1-9][0-9]*`, no suffix, value ≤ 2⁶³−1 | hex `0x1F`, octal `017`, `10u`/`10L`, floats |
| identifiers | `[A-Za-z_][A-Za-z0-9_]*` | universal character names |
| keywords | `int return if else while for break continue` | the other ~35 |
| comments | `// to end of line` | `/* block */` |
| other | | char/string literals, preprocessor (`#include`, `#define`) |

`007` is an **error** (in C it would be octal 7, which is confusing). `12abc` is an error, not `12` followed by `abc`.

## Types (ch 9)

- `int`: **64-bit signed**. This is the only deviation from C, because it keeps arm64 codegen to one register
  width (`x` registers everywhere). Overflow wraps (two's complement).
- `int *` and pointers to pointers: `&x`, `*p`, `p + n` scales by 8.
- `int a[N]`: fixed-size local arrays, `a[i]` means `*(a + i)`.

No `char`, `long`, `unsigned`, `void`, structs, unions, enums, typedef or casts.

## Expressions

From tightest to loosest binding:

| level | operators | assoc | ch |
|---|---|---|---|
| primary | literal, name, `f(args)`, `(e)`, `a[i]` | | 3, 8, 9 |
| unary | `-e` `!e` (later `&e` `*e`) | right | 4, 5, 9 |
| multiplicative | `*` `/` `%` | left | 3 |
| additive | `+` `-` | left | 3 |
| relational | `<` `<=` `>` `>=` | left | 5 |
| equality | `==` `!=` | left | 5 |
| logical and | `&&` (short-circuit) | left | 5 |
| logical or | `\|\|` (short-circuit) | left | 5 |
| assignment | `=` (target: name, `*p`, `a[i]`) | right | 6 |

- Comparisons and `! && ||` produce `0` or `1`.
- `/` truncates toward zero, and `%` takes the sign of the left operand (as in C). Division by zero traps.
- Operands and arguments are evaluated **left to right** (C leaves the order unspecified).
- Not included: `++ --`, `+= -=`, `?:`, `,`, bitwise `& | ^ ~ << >>`, `sizeof`.

## Statements (ch 6–7)

```c
int x;              int x = e;          // one variable per declaration
e;                  ;                   // expression statement, empty statement
return e;
{ ... }                                 // block = new scope (shadowing allowed)
if (e) s            if (e) s else s     // else binds to the nearest if
while (e) s
for (init; cond; step) s                // init: declaration or expression; any part may be empty
break;              continue;
```

Not included: `do/while`, `switch`, `goto` and labels.

## Functions and programs (ch 8, 10)

```c
int putchar(int c);                // declaration: needed before calling a function defined later or in libc
int add(int a, int b) { return a + b; }
int main() { putchar(48 + add(2, 3)); return 0; }
```

- All functions return `int` and take at most 8 `int`/pointer parameters (AAPCS64 registers `x0`-`x7`).
- A function must be declared or defined before it is called (as in C99+). Recursion works.
- Globals (ch 10): `int g;`, `int g = 5;` and arrays `int tape[30000];`, zero-initialized. An initializer
  must be a literal.
- The program's result is `main`'s return value. As a process exit code you see only the low 8 bits.
- I/O is `putchar` and `getchar` from libc (declare them: `int putchar(int c);` and `int getchar();`).
  `getchar` returns `-1` at end of input. You'll write `print_int` *in mini-C* as a chapter 8 exercise.

## Turing completeness

mini-C is Turing complete in the same sense C is, that is, up to available memory:

- **ch 7:** `while` + `if` + integer variables can already simulate any counter machine (in theory).
- **ch 10:** global arrays give real working memory, and `getchar`/`putchar` give I/O. The chapter 10
  capstone is a **Brainfuck interpreter written in mini-C**, compiled by your compiler, running Brainfuck
  programs read from stdin. Brainfuck is Turing complete, so if mini-C can run it, mini-C is too. This is
  the course's proof by construction. A reference version is in
  [`examples/bf.c`](examples/bf.c). It is valid C too: `clang examples/bf.c` runs the same way.

The limits are honest ones: 64-bit integers, fixed-size arrays and stack depth, the same as C on a real
machine. There is no `malloc` (it would need `void *` and casts). A big global array used as a heap is
enough, and a ★ extension can add a bump allocator on top of one.

## Errors

The compiler stops at the first error and prints `file:line:col: error: message`, then exits with status 1.
Mandatory checks: lexical errors, syntax errors, undeclared or redeclared names (ch 6), calls with the wrong
number of arguments (ch 10), `break`/`continue` outside a loop (ch 7).

## Extensions (★ chapter 11, pick any)

The cut features make good self-contained challenges: hex/octal literals, `/* */` comments, `++`/`+=`,
`?:`, bitwise operators, `char` and string literals, `do/while`, structs, `sizeof`, an IR with constant folding,
register allocation, and finally compiling your own compiler, which needs most of the above.
