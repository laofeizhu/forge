Use two indices: one starting at the left end, one at the right end. Swap, then move them toward each other.
---
Stop when they meet or cross: `while (i < j)`.
---
To avoid the `n - 1` trap, start with `size_t i = 0, j = n;` and use `arr[j - 1]`, or return early if `n == 0`.
