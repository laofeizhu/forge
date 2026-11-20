```c
const char *src = "int main() { return 42; }";
const char *p = src;
```

The scanner does, in order: skip whitespace + match `int`, skip whitespace + match `main`,
skip whitespace + match `(`, then `)`, then `{`.

What is `p - src` now?
