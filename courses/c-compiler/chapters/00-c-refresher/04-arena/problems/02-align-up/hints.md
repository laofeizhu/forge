`align_up` is the formula from the lesson: `(x + align - 1) & ~(align - 1)`.
---
A power of two has exactly one bit set. Subtracting 1 turns that bit off and every lower bit on: `8 = 1000`, `7 = 0111`. What is `x & (x - 1)` for a power of two?
---
Don't forget 0 is not a power of two: `x != 0 && (x & (x - 1)) == 0`.
