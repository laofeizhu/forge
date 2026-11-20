```c
size_t align_up(size_t x, size_t align);   // smallest multiple of align that is >= x
int    is_pow2(size_t x);                  // 1 if x is a power of two (1, 2, 4, ...), else 0
```

`align` is always a power of two.

**Example 1**
```
align_up(13, 8) → 16      align_up(16, 8) → 16      align_up(0, 16) → 0
```

**Example 2**
```
is_pow2(8) → 1     is_pow2(12) → 0     is_pow2(0) → 0
```

**Constraints**
- No loops — use bit operations.
