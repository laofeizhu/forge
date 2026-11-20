    .globl _main
    .p2align 2
_main:
    mov x0, #4
    mov x1, #3
    add x0, x0, x1      // x0 = 7
    mov x1, #6
    mul x0, x0, x1      // x0 = 42
    ret
