On arm64 macOS, what does this print? Type the three numbers separated by spaces.

```c
char s[] = "hello";
char *p = s;
printf("%zu %zu %zu\n", sizeof s, sizeof p, strlen(p));
```
