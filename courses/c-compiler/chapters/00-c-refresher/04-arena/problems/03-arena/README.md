Build the allocator your compiler will use for every token and AST node.

```c
typedef struct { unsigned char *base; size_t cap; size_t used; } Arena;

int   arena_init(Arena *a, size_t cap);                     // malloc cap bytes; 1 on success
void *arena_alloc(Arena *a, size_t size, size_t align);     // zeroed, aligned block or NULL
char *arena_strndup(Arena *a, const char *s, size_t n);     // copy n chars + '\0' into the arena
void  arena_reset(Arena *a);                                // forget everything, keep the memory
void  arena_free(Arena *a);                                 // release memory, reset to {0}
```

**Rules for `arena_alloc`**
- `align` is a power of two, at most 16. The returned pointer is a multiple of `align`.
- The returned memory is **zero-filled** (a fresh AST node should start with NULL children).
- If the block doesn't fit, return `NULL` and leave `used` unchanged.
- `size >= 1`.

**Example 1**
```
Arena a; arena_init(&a, 64);
char *c = arena_alloc(&a, 1, 1);    → a.used == 1
long *l = arena_alloc(&a, 8, 8);    → l == a.base + 8, a.used == 16
```

**Example 2**
```
arena_alloc(&a, 100, 8)             → NULL (only 64 bytes total), a.used still 16
arena_strndup(&a, "main(void)", 4)  → "main"
```

**Constraints**
- One `malloc` in `arena_init`, one `free` in `arena_free`. No other heap calls.
- You may copy `align_up` from the previous problem.
