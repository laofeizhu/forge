```c
#define ALIGN_UP(x, a) (((x) + ((a) - 1)) & ~((a) - 1))
printf("%d %d %d\n", ALIGN_UP(13, 8), ALIGN_UP(16, 8), ALIGN_UP(17, 8));
```

What does this print? (three numbers separated by spaces)
