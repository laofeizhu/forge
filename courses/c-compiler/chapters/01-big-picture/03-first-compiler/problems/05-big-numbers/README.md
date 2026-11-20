★ Lift the 65535 limit: support every mini-C literal, `0 … 9223372036854775807` (2⁶³ − 1).

An instruction can only carry 16 bits, so build the 64-bit value 16 bits at a time:

```
movz x0, #c0              x0 = c0                      (z: zero the other bits)
movk x0, #c1, lsl #16     bits 16-31 = c1              (k: keep the other bits)
movk x0, #c2, lsl #32
movk x0, #c3, lsl #48
```

where `c0` is bits 0-15 of the value, `c1` bits 16-31, and so on. Format (unit-tested):

- `value ≤ 65535`: keep the single `mov x0, #value` line (so 1.3-02's tests still pass).
- otherwise: one `movz x0, #c0`, then a `movk` line **only for each non-zero** chunk k = 1, 2, 3.
  Chunks are written in decimal.

```
70000 = 0x0001_1170  →  movz x0, #4464
                         movk x0, #1, lsl #16
```

And in `compile`: accept the bigger numbers, but **reject overflow**. `9223372036854775808` doesn't
fit in a `long`. Check *before* the multiply-add would overflow (signed overflow is undefined behaviour,
and the sanitizer will tell you if you get it wrong).

**Trace these before you submit**

| source | expect |
|---|---|
| `return 4294967296;` (2³²) | exit 0, chunks 0, 0, 1, 0 |
| `return 9223372036854775807;` | exit 255 (low 8 bits all ones) |
| `return 9223372036854775808;` | error |
| `return 99999999999999999999999;` | error, without overflowing |
