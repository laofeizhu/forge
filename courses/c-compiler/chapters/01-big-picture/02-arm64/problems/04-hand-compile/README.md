Be the compiler. Write, by hand, the arm64 program that `int main() { return (4 + 3) * 6; }` would
compile to, **computing** the value with `add` and `mul` (not `mov x0, #42`).

Rules from the lesson:

- `mul` takes registers only, so the 6 must be in a register first.
- the result must end up in `x0` before `ret`.
- keep `.globl _main`, `.p2align 2` and the `_main:` label.

`:w` assembles your file with `cc` and runs it. Trace your register table first: what's in `x0`, `x1`
after each line?
