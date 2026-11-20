Implement

```c
void reverse(int *arr, size_t n);
```

which reverses the first `n` elements of `arr` **in place** (no second array).

**Example 1**
```
arr = [1, 2, 3, 4, 5], n = 5   →   arr = [5, 4, 3, 2, 1]
```

**Example 2**
```
arr = [1, 2], n = 2   →   arr = [2, 1]
```

**Constraints**
- `0 <= n <= 100000`. When `n == 0`, `arr` may be `NULL`.
- Don't allocate memory.

> Watch out: `size_t` is **unsigned**. `n - 1` when `n == 0` is not `-1`, it is a huge number.
> The sanitizer will tell you if you walk off the end of the array.
