You need somewhere to keep one value while you overwrite it: a temporary `int`.
---
`int tmp = *a;` — now `*a` is safe to overwrite with `*b`.
