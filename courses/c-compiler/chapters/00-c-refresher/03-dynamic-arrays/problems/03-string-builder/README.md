Your code generator will build its whole assembly output in one of these.

```c
typedef struct { char *data; size_t len; size_t cap; } StrBuf;

void sb_append_n(StrBuf *sb, const char *s, size_t n);  // append exactly n chars from s
void sb_append(StrBuf *sb, const char *s);              // append a NUL-terminated string
void sb_append_char(StrBuf *sb, char c);
const char *sb_cstr(StrBuf *sb);                         // contents as a C string
void sb_free(StrBuf *sb);                                // free and reset to {0}
```

**Rules**
- After any append, `data[len] == '\0'` (so the buffer is always a valid C string).
- `sb_cstr` on an empty `{0}` buffer returns `""` (never NULL).
- `len` never counts the terminator.

**Example 1**
```
StrBuf sb = {0};
sb_append(&sb, "mov x0, ");
sb_append(&sb, "#42");
sb_append_char(&sb, '\n');
→ sb_cstr(&sb) == "mov x0, #42\n",  sb.len == 12
```

**Example 2**
```
sb_append_n(&sb, "return;", 6)   →  appends "return" (6 chars, no ';')
```

**Constraints**
- Grow geometrically (doubling); appending a 1 MB total of single chars must be fast.
- Don't use `strcat`. `memcpy` and `strlen` are fine.
