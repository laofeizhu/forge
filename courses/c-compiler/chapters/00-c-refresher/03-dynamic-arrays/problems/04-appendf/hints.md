`vsnprintf(NULL, 0, fmt, ap)` returns how many characters the result *would* need, without writing anything.
---
So: measure, `sb_reserve` that many, then `vsnprintf` again into `sb->data + sb->len` with `cap - len` room.
---
A `va_list` can only be walked once. Make a copy with `va_copy(ap2, ap)` before the first `vsnprintf`, use the copy for measuring, and `va_end` both.
