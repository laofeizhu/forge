Return **two** values from one function using out-parameters:

```c
int min_max(const int *arr, size_t n, int *out_min, int *out_max);
```

- If `n == 0`, return `0` and **don't touch** `*out_min` / `*out_max`.
- Otherwise store the smallest element in `*out_min`, the largest in `*out_max`, and return `1`.

**Example 1**
```
arr = [3, -1, 7, 2], n = 4   →  returns 1, *out_min = -1, *out_max = 7
```

**Example 2**
```
arr = [], n = 0              →  returns 0, out values unchanged
```

This "return a status, write results through pointers" shape is how your lexer and parser
will report both *what* they found and *whether* they succeeded.
