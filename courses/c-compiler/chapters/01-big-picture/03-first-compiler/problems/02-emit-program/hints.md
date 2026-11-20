Two `sb_append` calls for the fixed lines, one `sb_appendf(out, "    mov x0, #%ld\n", value)`, one more for `ret`.
---
Appending means never touching `out->len` or `out->data` yourself: the sb_ functions handle it.
---
Compare character by character with the README: four spaces before each instruction, none before `_main:`.
