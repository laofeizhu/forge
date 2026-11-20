# 0.3 Structs & growable arrays

Your compiler doesn't know in advance how many tokens a file has, or how many lines of assembly it
will emit. It needs arrays that **grow**. C doesn't have them — so you build one.

## Structs bundle related values

```c
typedef struct {
    int   *data;   // the elements, on the heap
    size_t len;    // how many are in use
    size_t cap;    // how many fit before we must grow
} IntVec;

IntVec v = {0};    // all fields zero: data = NULL, len = 0, cap = 0 — a valid empty vec
```

Through a pointer, use `->`:  `v_ptr->len` is shorthand for `(*v_ptr).len`.

## The heap: malloc, realloc, free

```c
int *a = malloc(8 * sizeof(int));        // room for 8 ints, uninitialized
a = realloc(a, 16 * sizeof(int));        // now room for 16; old contents are kept
free(a);                                 // give it back; `a` is now dangling — don't use it
```

`realloc(NULL, n)` behaves like `malloc(n)` — handy, because an empty vec has `data == NULL`.

## Growing by doubling

Picture `len` and `cap`:

```
cap = 4      ┌───┬───┬───┬───┐
len = 4      │ 3 │ 1 │ 4 │ 1 │   full! push(5) →  realloc to cap 8, then store
             └───┴───┴───┴───┘
cap = 8      ┌───┬───┬───┬───┬───┬───┬───┬───┐
len = 5      │ 3 │ 1 │ 4 │ 1 │ 5 │   │   │   │
             └───┴───┴───┴───┴───┴───┴───┴───┘
```

If you grew by 1 each time, pushing *n* items would copy about *n²/2* elements. Doubling means each
element is copied only about twice on average — pushes are **amortized O(1)**.

```c
if (v->len == v->cap) {
    v->cap = v->cap ? v->cap * 2 : 8;
    v->data = realloc(v->data, v->cap * sizeof *v->data);
}
v->data[v->len++] = x;
```

## A string builder is the same idea for chars

Your code generator will emit assembly one line at a time into a growing `char` buffer — a *string
builder*. The only twist: keep a `'\0'` after the last character so the buffer is always a valid
C string. That means you always need `cap >= len + 1`.
