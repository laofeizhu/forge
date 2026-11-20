Write one helper first: `static void sb_reserve(StrBuf *sb, size_t extra)` that makes sure `cap >= len + extra + 1` (the +1 is the terminator).
---
In `sb_reserve`, double `cap` (starting from something like 16) in a loop until it's big enough, then `realloc` once.
---
`sb_append` is `sb_append_n(sb, s, strlen(s))`; `sb_append_char` is `sb_append_n(sb, &c, 1)`. For `sb_cstr` on an empty buffer, return a string literal `""`.
