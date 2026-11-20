# 0.4 Arena allocation

A compiler allocates *thousands* of tiny objects — tokens, AST nodes, type records — and they all
die together when compilation ends. Calling `malloc`/`free` for each one is slow and error-prone.

**An arena** grabs one big block up front and hands out pieces by bumping a counter:

```
base                                                   base + cap
 │                                                          │
 ▼                                                          ▼
 ┌──────────┬────┬───────────────┬──────────────────────────┐
 │ Node (24)│pad │  Token (32)   │      free space ...      │
 └──────────┴────┴───────────────┴──────────────────────────┘
                                 ▲
                               used        next alloc starts here (after alignment)
```

- **alloc** = round `used` up to the alignment, return `base + used`, add `size` to `used`.
- **free one object**: you don't. Ever.
- **free everything**: `used = 0` (reset) or `free(base)` once. No leaks, no double-frees.

## Alignment

On arm64, an 8-byte `long` or pointer should live at an address divisible by 8. Misaligned data is
slower and, for some instructions, illegal. So before handing out memory for an object with
alignment `A`, round the offset **up** to the next multiple of `A`.

`_Alignof(T)` (C11) gives a type's required alignment. On arm64 macOS:

| type | `sizeof` | `_Alignof` |
|---|---|---|
| `char` | 1 | 1 (any address works) |
| `int` | 4 | 4 |
| `long`, `size_t`, pointers | 8 | 8 |
| `struct { char c; long l; }` | 16 | 8 (its strictest field) |

For `A` a power of two (1, 2, 4, 8, 16), there's a classic bit trick:

```c
(x + (A - 1)) & ~(A - 1)
```

```
x = 13, A = 8:      13 + 7 = 20 = 0b10100
                   ~(8-1)       = 0b...11000
                   20 & ~7      = 0b10000 = 16
```

Adding `A - 1` pushes `x` past the next boundary *unless* it's already on one; masking off the low
bits snaps it back down to that boundary. `x = 16` stays 16. `x = 0` stays 0.

## Why this matters later

`sizeof` and `_Alignof` are things **your** compiler will compute (chapter 9 and 11): struct layout
is exactly this arithmetic — each field's offset is the previous end rounded up to the field's
alignment.
