In `src/codegen.c`, implement

```c
void emit_program(StrBuf *out, long value);
```

It **appends** this exact text to `out` (4-space indents, a newline after every line):

```
    .globl _main
    .p2align 2
_main:
    mov x0, #42
    ret
```

with `42` replaced by `value`. For this chapter `0 ≤ value ≤ 65535`.

**Example**

```
StrBuf out = {0};
emit_program(&out, 7);
sb_cstr(&out)  →  "    .globl _main\n    .p2align 2\n_main:\n    mov x0, #7\n    ret\n"
```

`sb_appendf` (you wrote it in 0.3-04) does the formatting. `%ld` prints a `long`.

**Trace these before you submit**

| case | expect |
|---|---|
| `value = 0` | `mov x0, #0` |
| `out` already holds text | your program goes **after** it |
