#include "min_max.h"

int min_max(const int *arr, size_t n, int *out_min, int *out_max) {
    if (n == 0) return 0;
    int lo = arr[0], hi = arr[0];
    for (size_t i = 1; i < n; i++) {
        if (arr[i] < lo) lo = arr[i];
        if (arr[i] > hi) hi = arr[i];
    }
    *out_min = lo;
    *out_max = hi;
    return 1;
}
