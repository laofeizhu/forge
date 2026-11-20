## What a compiler does, in one picture

Follow one program all the way down. Every stage turns one representation into the next:

```
 source      int main() { return 42; }          a string of chars
   │ lexer (ch 2)
   ▼
 tokens      int  main  (  )  {  return  42  ;  }
   │ parser (ch 3)
   ▼
 AST         Function main
               └─ Return
                    └─ Num 42
   │ code generator (ch 4+)
   ▼
 assembly        .globl _main
                 .p2align 2
             _main:
                 mov x0, #42
                 ret
   │ cc (assembler + linker: borrowed, not written)
   ▼
 executable  ./prog  → runs → exit code 42
```

**You write the first three arrows.** The assembler and linker already exist: `cc out.s -o prog` turns your
text into a runnable program. Your compiler's whole job is *producing the right text*.

### Which stage catches which mistake?

| mistake | caught by | why |
|---|---|---|
| `int x = 3$;` | lexer | `$` isn't any token |
| `return 42` (no `;`) | parser | every token is fine; the *order* is wrong |
| `return y;` with no `y` | semantic check (ch 6) | grammatically fine, but `y` doesn't exist |
| `mov x0, #70000` | assembler | your compiler emitted an instruction that can't exist (ch 1.3★) |

### The exit code: your first output channel

Until chapter 8 (`putchar`), the only thing your programs can "say" is `main`'s return value. The shell
shows it as `$?`:

```
$ ./prog; echo $?
42
```

**Contract: exit codes are 8 bits.** The OS keeps only the low 8 bits, `value & 255`:

```
return 42;    → 42
return 256;   → 0        256 = 1_0000_0000₂ → low 8 bits 0000_0000
return 300;   → ?        (you'll compute this in a moment)
```

Tests in this course compile a program with **your** compiler, run it and compare the exit code.

### Try it (optional, in a terminal)

```
$ printf 'int main() { return 42; }' > r.c
$ clang -S -O0 -o - r.c
```

clang prints ~20 lines: `.cfi_*`, `.build_version`, a stack frame. Almost all of it is bookkeeping.
The 5 lines in the picture above are the part that matters, and they're all you need to emit.
