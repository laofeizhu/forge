An empty `IntVec v = {0}` grows with this rule: when `len == cap`, set `cap = cap ? cap * 2 : 8`
and `realloc`.

You push 100 ints. **How many times is `realloc` called?**
