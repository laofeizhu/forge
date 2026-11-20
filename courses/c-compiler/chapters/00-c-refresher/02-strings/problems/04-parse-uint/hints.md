Keep a local cursor `const char *p = s;` and the running value `long n = 0;`.
---
For each digit: `n = n * 10 + (*p - '0'); p++;`
---
After the loop, `p == s` means you read no digits. Always finish with `*end = p;`.
