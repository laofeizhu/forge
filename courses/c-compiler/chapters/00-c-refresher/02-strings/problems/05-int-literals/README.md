Real C has three ways to write an integer. Parse all of them:

| form | example | value |
|---|---|---|
| decimal: starts with `1-9` (or is just `0`) | `42` | 42 |
| hexadecimal: `0x` or `0X` then hex digits `0-9a-fA-F` | `0x1F` | 31 |
| octal: `0` then octal digits `0-7` | `017` | 15 |

```c
size_t parse_int_literal(const char *s, unsigned long *out);
```

Return the number of characters consumed and store the value in `*out`.
Return `0` (and leave `*out` alone) if `s` doesn't start with a **valid** literal:

- no digit at the start, or `0x` with no hex digits after it
- an octal literal containing `8` or `9` (`019`)
- the literal is immediately followed by a letter, digit or `_` (`12abc`, `0x1g`) — we don't support suffixes

**Example 1**
```
"0x1F)"  →  returns 4, *out = 31
```

**Example 2**
```
"017"    →  returns 3, *out = 15
"019"    →  returns 0
```

**Constraints**
- Values fit in `unsigned long`.
