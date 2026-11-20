Since `malloc` returns memory aligned to 16, aligning the *offset* `used` is enough to align the pointer.
---
`size_t start = align_up(a->used, align); if (start + size > a->cap) return NULL;`
---
Then `void *p = a->base + start; memset(p, 0, size); a->used = start + size; return p;`
---
`arena_strndup`: allocate `n + 1` bytes with align 1, `memcpy` n chars; the zero-fill already gave you the `'\0'`.
