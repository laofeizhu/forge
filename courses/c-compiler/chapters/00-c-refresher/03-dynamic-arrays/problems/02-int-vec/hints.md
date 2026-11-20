Check `v->len == v->cap` at the top of `vec_push`. That's also true for a brand-new `{0}` vec — which is exactly when you allocate the first time.
---
`realloc(NULL, size)` is `malloc(size)`, so one call handles both first allocation and growth.
---
`vec_pop`: `return v->data[--v->len];`. `vec_free`: `free(v->data); *v = (IntVec){0};`
