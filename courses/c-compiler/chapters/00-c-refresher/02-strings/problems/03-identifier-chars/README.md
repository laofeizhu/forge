A C identifier (like `main`, `_tmp`, `x2`) starts with a letter or underscore and continues with
letters, digits, or underscores. Implement the two predicates your lexer will use:

```c
int is_ident_start(char c);  // 1 if c can start an identifier: a-z A-Z _
int is_ident_char(char c);   // 1 if c can continue one:        a-z A-Z _ 0-9
size_t ident_len(const char *s);  // length of the identifier at the start of s (0 if none)
```

**Example 1**
```
is_ident_start('_') → 1     is_ident_start('7') → 0
is_ident_char('7')  → 1     is_ident_char('+')  → 0
```

**Example 2**
```
ident_len("count+1") → 5
ident_len("9lives")  → 0     (can't start with a digit)
```

**Constraints**
- Don't use `<ctype.h>` — do the comparisons yourself (that's the point).
- Return exactly `0` or `1`.
