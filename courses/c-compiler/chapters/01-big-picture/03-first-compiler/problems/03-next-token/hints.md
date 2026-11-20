Start with `const char *s = *p;` and work with `s`; write `*p = ...` once at the end. Fewer `*` to get wrong.
---
Skip: `while (*s == ' ' || *s == '\t' || *s == '\n' || *s == '\r') s++;` Then `const char *start = s;`
and three cases: `*s == '\0'` (don't advance), a word char (advance while word chars), otherwise `s++` once.
---
`*len = (size_t)(s - start); *p = s; return start;` A word char test: `isalnum((unsigned char)c) || c == '_'`.
