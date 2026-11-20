Codegen reads much better as `sb_appendf(&out, "  mov x0, #%ld\n", value);`. Add it:

```c
void sb_appendf(StrBuf *sb, const char *fmt, ...);
```

It formats like `printf` and appends the result. The rest of `StrBuf` is already implemented in
the starter (a reference version of the previous problem).

**Example 1**
```
sb_appendf(&sb, "  mov x0, #%d\n", 42)   →  "  mov x0, #42\n"
```

**Example 2**
```
sb_appendf(&sb, "%s:", "_main"); sb_appendf(&sb, "%s", "\n")   →  "_main:\n"
```

**Constraints**
- Any output length must work (tests format a 10,000-char string).
- Use `vsnprintf` — no fixed-size temporary buffer that could be too small.

This problem is about **variadic functions**: `...`, `va_list`, `va_start`, `va_end`, and the
one most people get wrong — `va_copy`.
