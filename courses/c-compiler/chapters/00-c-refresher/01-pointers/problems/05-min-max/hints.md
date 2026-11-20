Start both running values at `arr[0]` (only after checking `n > 0`), then loop from index 1.
---
Write to `*out_min` and `*out_max` once at the end, not `out_min = ...` (that changes your local copy of the pointer, not the caller's int).
