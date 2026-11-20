Parse the decimal number at the start of a string, and report where it stopped:

```c
long parse_uint(const char *s, const char **end);
```

- Read as many digits `0-9` as there are at the start of `s` and return their value.
- Set `*end` to point at the **first character after the number**.
- If `s` does not start with a digit, return `-1` and set `*end = s`.

**Example 1**
```
s = "123+4"   →  returns 123, *end points at "+4"
```

**Example 2**
```
s = "x1"      →  returns -1,  *end == s
```

**Constraints**
- At most 18 digits, so the result always fits in a `long`.
- No signs: `"-5"` is *not* a number here (`-` is a separate token in C).
- Don't use `strtol` / `atoi`.

`end` is a pointer *to a pointer*: you're giving the caller back a cursor. Your lexer will call
this, then continue lexing from `*end`.
