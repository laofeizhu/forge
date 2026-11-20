In `src/token.c`, implement

```c
const char *next_token(const char **p, size_t *len);
```

1. Skip whitespace (`' '`, `'\t'`, `'\n'`, `'\r'`) starting at `*p`.
2. Decide the token by its **first** char:
   - `'\0'`: end of input. Return a pointer to the `'\0'`, set `*len = 0`, and **don't move past it**.
   - `[A-Za-z0-9_]`: a word. It runs while chars are `[A-Za-z0-9_]`.
   - anything else: a one-char token (`(`, `)`, `{`, `}`, `;`, even `$`).
3. Set `*len`, move `*p` to just after the token, and return the token's start.

The token is a **slice of the source** (start + length), like `sb_append_n(s, n)` in 0.3: you return a
pointer *into* the string, you don't copy anything. That's why `*p` is a `const char **`: the function moves
*your* cursor, which it can only do through a pointer to it.

**Example** (`tok()` in the tests prints the slice with `"%.*s"`)

```
const char *p = "int main(){return 42;}";
next_token(&p, &len)   →  "int"     len 3
next_token(&p, &len)   →  "main"    len 4
next_token(&p, &len)   →  "("       len 1
...
next_token(&p, &len)   →  "}"       len 1
next_token(&p, &len)   →  ""        len 0,  *p points at the '\0'
```

**Trace these before you submit**

| source | tokens |
|---|---|
| `"\n\t  int\r\n"` | `int`, then end |
| `"intmain("` | `intmain`, `(` (one word, not two) |
| `"return42;"` | `return42`, `;` |
| `"a$b"` | `a`, `$`, `b` |
| `""` or `"   "` | end, immediately |
| at the end, call it 3 more times | end every time, `*p` doesn't move |
| `"int main"` | the 2nd token's pointer is `src + 4`, *inside* src |
