Implement

```c
void swap(int *a, int *b);
```

which exchanges the values of the two ints that `a` and `b` point to.

**Example 1**
```
int x = 1, y = 2;
swap(&x, &y);      →  x == 2, y == 1
```

**Example 2**
```
int arr[3] = {7, 8, 9};
swap(&arr[0], &arr[2]);   →  arr == {9, 8, 7}
```

**Constraints**
- `a` and `b` are never NULL.
- `a` and `b` may point to the **same** int — then nothing should change.
