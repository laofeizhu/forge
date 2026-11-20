#include "align.h"

size_t align_up(size_t x, size_t align) {
    return (x + align - 1) & ~(align - 1);
}

int is_pow2(size_t x) {
    return x != 0 && (x & (x - 1)) == 0;
}
