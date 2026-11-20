Compare a token with an expected word by **length and chars**: `n == strlen(s) && strncmp(t, s, n) == 0`.
Why isn't `strncmp(t, "int", 3) == 0` enough on its own? (Think `integer`.)
---
`compile` is a straight line: next_token + compare for `int`, `main`, `(`, `)`, `{`, `return`; then the
number token; then `;`, `}`; and finally the next token must be the end (length 0).
---
The number token: `n > 0`, every char a digit, not (`t[0] == '0'` and `n > 1`), value ≤ 65535.
For the error message, `fprintf(stderr, "error: expected '%s', got '%.*s'\n", want, (int)n, t)` prints the slice.
