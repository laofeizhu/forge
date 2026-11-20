#include "reverse.h"

void reverse(int *arr, size_t n) {
    if (n == 0) return;
    size_t i = 0, j = n - 1;
    while (i < j) {
        int tmp = arr[i];
        arr[i] = arr[j];
        arr[j] = tmp;
        i++;
        j--;
    }
}
