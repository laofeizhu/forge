## Your project: one compiler, growing every chapter

From here on, code problems edit **one** program: your compiler, `mcc`, in
`~/forge-work/c-compiler/project/`. Each problem adds a piece; nothing is thrown away.

```
project/
  Makefile         make → ./mcc     make try P=prog.c → compile, run, print the exit code
  src/mcc.h        every interface (the course fixes signatures, tests call them)
  src/main.c       the driver, provided: read file → compile() → write .s
  src/strbuf.c     your 0.3 string builder (reference version)
  src/codegen.c    1.3-02 emit_program()
  src/token.c      1.3-03 next_token()
  src/compile.c    1.3-04 compile()
```

Warnings are errors from now on (`-Werror`): a warning fails the build, so it can't scroll past.

## The driver, and who owns what

`main.c` is ~50 lines; read it once. The flow:

```
main(argc, argv)
  ├─ src = read_file(in)          malloc'd buffer: main owns it → free(src)
  ├─ compile(src, &asm_text)      appends assembly to a StrBuf = {0}
  ├─ free(src)                    done with the source
  ├─ write sb_cstr(&asm_text) to the .s file
  └─ sb_free(&asm_text)
```

**Ownership rule used everywhere in mcc:** whoever allocates documents who frees. `read_file` hands
its buffer *to the caller* (`return sb.data`: the pointer leaves, the StrBuf struct is dropped).
`compile` only *appends* to a StrBuf it was given; it never frees it.

## Chapter 1's compiler is a pattern matcher

No real parser yet. `compile()` accepts exactly one shape:

```
int main ( ) { return N ; }       with any whitespace (or none) between the pieces
```

and emits the program from 1.2 with `N` in it. Anything else → print `error: …` to stderr, return 1.

Walk the source with a **cursor**, like `parse_uint`'s end pointer in 0.2:

```
src:   i n t ␣ m a i n ( ) ␣ { ␣ r e t u r n ␣ 4 2 ; ␣ }
       0 1 2 3 4 5 6 7 8 9 …
       ↑ p                       skip whitespace, match "int"  → p = src + 3
             ↑ p                 skip whitespace, match "main" → p = src + 8
```

Instead of matching raw text, cut the source into **tokens** first: a tiny lexer, `next_token()`
(1.3-03). Then `compile()` (1.3-04) just asks for tokens one by one and checks each is the expected one.

### A token is a slice

`next_token` doesn't copy anything. A token is *where it starts* + *how long it is*, pointing into the
source (the pointer + length style of `sb_append_n` and `arena_strndup`):

```
src:  "int main(){return 42;}"
       ^^^                      start = src + 0, len 3   "int"
           ^^^^                 start = src + 4, len 4   "main"
                         ^^     start = src + 18, len 2  "42"
```

### Where does a token end? Decide by its first char

```
skip whitespace
'\0'           → end of input (len 0); never move past it
[A-Za-z0-9_]   → a word: take chars while they're [A-Za-z0-9_]
anything else  → a one-char token: ( ) { } ;
```

This one rule makes `intmain` a single word (≠ `int`, so `compile` rejects it) and `return42` a single
word, with no special cases. That's also how real C lexers decide.

### Numbers follow mini-C's rules (0.2-05)

`0`, or a non-zero digit followed by digits. `007` is an error. For chapter 1, `N ≤ 65535` (the 16-bit
immediate limit from 1.2; the ★ problem lifts it). A number is a word, so `42abc` is one token and
not a number.
