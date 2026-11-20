Letters are two ranges: `c >= 'a' && c <= 'z'` and `c >= 'A' && c <= 'Z'`.
---
`is_ident_char` is `is_ident_start(c)` *or* a digit — reuse it.
---
`ident_len`: if the first char isn't a start char, return 0; otherwise count while `is_ident_char`.
