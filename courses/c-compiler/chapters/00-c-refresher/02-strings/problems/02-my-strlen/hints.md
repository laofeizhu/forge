Walk a pointer (or an index) forward until the character is `'\0'`.
---
Pointer version: `const char *p = s; while (*p) p++; return p - s;`
