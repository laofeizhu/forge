Decide the base first by looking at the first one or two characters, then run one shared loop: `n = n * base + digit_value(c)`.
---
Write `int digit_value(char c)` that returns 0-15 for `0-9a-fA-F` and -1 otherwise. A digit is valid for a base if `0 <= value < base`.
---
After the loop, reject if the next character is an identifier character or a digit (that covers `019`, `12abc`, `0x1g`).
---
`"0"` on its own is fine: it's an octal literal with no extra digits.
