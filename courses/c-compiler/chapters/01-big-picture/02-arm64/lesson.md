## Registers: 31 boxes that hold a number

arm64 has 31 general-purpose registers, `x0` … `x30`, each holding one 64-bit value. `w0` names the
low 32 bits of `x0` (same box, narrower view). There's also `sp`, the stack pointer (chapter 6).

**`x0` is the return value.** When `main` executes `ret`, whatever is in `x0` becomes the exit code.

## Five instructions are enough for now

Destination comes **first**, like an assignment:

| instruction | means | |
|---|---|---|
| `mov x0, #5` | `x0 = 5` | `#` = an immediate (a constant in the instruction) |
| `mov x0, x1` | `x0 = x1` | **copies the value**; afterwards they're unrelated |
| `add x0, x1, x2` | `x0 = x1 + x2` | the last operand may be `#imm` |
| `sub x0, x1, #2` | `x0 = x1 - 2` | |
| `mul x0, x1, x2` | `x0 = x1 * x2` | registers only, no `#imm` |
| `ret` | return to the caller | `x0` is the result |

## Trace it like memory: one row per instruction

The same brain simulation you did for pointers works for registers. Keep a table:

```
                    x0   x1
mov x0, #5           5    ?
mov x1, #7           5    7
add x0, x0, x1      12    7
ret                 → exit code 12
```

## The whole program

```
    .globl _main        // export the symbol: the linker looks for _main
    .p2align 2          // align to 2² = 4 bytes: every arm64 instruction is 4 bytes
_main:                  // a label: the address of the next instruction
    mov x0, #42
    ret
```

- **`_main`, not `main`:** on macOS every C-level name gets a leading `_` at the assembly level.
  `main` in C is `_main` here, and later `putchar` is `_putchar`.
- **`.p2align 2`** is `align_up(offset, 4)` from 0.4, done by the assembler.
- Lines starting with `.` are **directives** (instructions *to the assembler*); the rest become machine code.

## Contract: an immediate is a 16-bit chunk

Every instruction is exactly 32 bits, so a constant inside one has to be small. `mov x0, #N` works for
`0 ≤ N ≤ 65535` (and a few special patterns). `mov x0, #70000` is an **assembler error**. Real compilers
build big numbers 16 bits at a time with `movz`/`movk`, which is the ★ problem at the end of this chapter.

## Try it (optional)

```
$ cat > a.s                  # paste the program above, then ctrl-d
$ cc a.s -o a && ./a; echo $?
42
```
