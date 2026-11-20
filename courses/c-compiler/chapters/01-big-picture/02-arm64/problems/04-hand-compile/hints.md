Get 4 and 3 into registers (`mov`), add them, then get 6 into a register and multiply.
---
```
mov x0, #4
mov x1, #3
add x0, x0, x1      // x0 = 7
mov x1, #6
...                 // x0 = x0 * x1
```
---
`mul x0, x0, x1`, then `ret`.
