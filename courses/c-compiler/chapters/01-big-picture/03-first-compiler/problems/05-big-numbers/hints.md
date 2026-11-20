Chunk k is `(value >> (16 * k)) & 0xFFFF`. Draw 70000 in hex first: 0x11170, so c0 = 0x1170 = 4464, c1 = 1.
---
Overflow check before `n = n * 10 + d`: it overflows exactly when `n > (LONG_MAX - d) / 10`
(`LONG_MAX` is in `<limits.h>`). Trace it with n = 922337203685477580 and d = 7, then d = 8.
---
With the bigger range the old `n > 65535` check goes away; everything else in compile() stays.
