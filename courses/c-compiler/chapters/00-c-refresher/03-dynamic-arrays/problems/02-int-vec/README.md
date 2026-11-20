Implement a growable array of ints (the struct is in `vec.h`):

```c
typedef struct { int *data; size_t len; size_t cap; } IntVec;

void vec_push(IntVec *v, int x);   // append x, growing if needed
int  vec_pop(IntVec *v);           // remove and return the last element (len > 0 guaranteed)
void vec_free(IntVec *v);          // free memory and reset to {0}
```

**Growth rule** (tests check it): when `len == cap`, new `cap = cap ? cap * 2 : 8`.

**Example 1**
```
IntVec v = {0};
vec_push(&v, 10); vec_push(&v, 20);
→ v.len == 2, v.cap == 8, v.data[0] == 10, v.data[1] == 20
```

**Example 2**
```
push 1..9   →  v.cap == 16
vec_pop(&v) →  returns 9, v.len == 8
vec_free(&v) → v.data == NULL, v.len == 0, v.cap == 0
```

**Constraints**
- `vec_free` on an empty `{0}` vec must be safe.
- A freed vec must be reusable (push again after free).
