# 0.1 Pointers & memory

A compiler spends its whole life walking through memory: source text, tokens, tree nodes.
So we start where C starts — **memory is one long row of numbered boxes.**

```
address:  1000  1004  1008  1012
         ┌─────┬─────┬─────┬─────┐
int a[4] │ 10  │ 20  │ 30  │ 40  │
         └─────┴─────┴─────┴─────┘
           a[0]  a[1]  a[2]  a[3]
```

Each `int` is 4 bytes, so the boxes are 4 addresses apart.

## A pointer is just an address

```c
int x = 7;
int *p = &x;   // &x  = "the address of x"      → p holds 1000 (say)
*p = 9;        // *p  = "the box p points at"   → x is now 9
```

Read `int *p` as "`*p` is an int". Two operators, two directions:

| you have | you want | write |
|---|---|---|
| a variable `x` | its address | `&x` |
| an address `p` | the value there | `*p` |

## Pointer arithmetic counts *elements*, not bytes

```c
int *p = a;     // p → a[0]   (an array name turns into a pointer to its first element)
p + 1           // → a[1]     (address 1004: the compiler multiplies by sizeof(int))
*(p + 2)        // == a[2] == 30
p[2]            // exactly the same thing: p[i] means *(p + i)
```

## Why functions take pointers

C passes arguments **by value**: a function gets a *copy*. To change the caller's variable,
pass its address:

```c
void set_to_zero(int *n) { *n = 0; }

int count = 5;
set_to_zero(&count);   // count is now 0
```

This is also how C "returns" more than one value — through **out-parameters**. You will use
this pattern constantly: `parse_number(text, &end)` returns a number *and* tells you where it
stopped reading.

## `sizeof` is about types, not contents

On arm64, `sizeof(int) == 4`, `sizeof(long) == 8`, and **every pointer is 8 bytes**.
`sizeof` is computed by the compiler from the *type* — it never looks at what's stored.

```c
char s[] = "hi";   // an array of 3 chars: 'h' 'i' '\0'   → sizeof s == 3
char *t = s;       // a pointer                           → sizeof t == 8
```

Your compiler will compute these sizes itself in chapter 9. Now: the problems.
