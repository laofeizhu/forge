In `src/compile.c`, implement

```c
int compile(const char *src, StrBuf *out);
```

Use your `next_token()` from 1.3-03: `compile` reads tokens one by one and checks each is the expected one.

- If `src` is exactly `int main ( ) { return N ; }` (whitespace allowed anywhere *between* pieces,
  including before and after), call `emit_program(out, N)` and return `0`.
- Otherwise print one line `error: <what you expected>` to **stderr** and return `1`.
  Wording is up to you, e.g. `error: expected ';'`.

`N` follows mini-C: `0` or `[1-9][0-9]*`, at most 65535.

The tests build the whole project (`make` does the same), compile each program with **your** `mcc`,
assemble it, run it and check the exit code. For a rejected program they check that `mcc` exits non-zero.

**Trace these before you submit** (they are the hidden tests)

| source | expect |
|---|---|
| `int\nmain\t(\n)\n{\n    return 255;\n}` | exit code 255 |
| `int main() { return 0; }` (no trailing newline) | exit code 0 |
| `\n\n   int main() { return 3; }   \n\n` | exit code 3 |
| `intmain() { return 1; }` | error: `intmain` is one word |
| `int main() { return42; }` | error: `return42` is one word |
| `int main() { return 007; }` | error: leading zero |
| `int main() { return x; }` | error: not a number |
| `int main() { return 1; } }` | error: junk after the program |
| *(empty file)* | error |
| `int main() { return 1;` | error: cut short (next_token gives end where `}` should be) |
| `int main() { return 42abc; }` | error: `42abc` is one word, not a number |

Play with it: in the project directory, `make try P=prog.c`, or `./mcc prog.c -o -` to see the assembly.
