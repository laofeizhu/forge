#include "forge_test.h"
#include "reverse.h"
#include <stdlib.h>

TEST(empty_null_array) {
    reverse(NULL, 0);
    ASSERT_TRUE(1);
}

TEST(single_element) {
    int *arr = malloc(sizeof(int));
    arr[0] = 9;
    reverse(arr, 1);
    ASSERT_EQ_INT(arr[0], 9);
    free(arr);
}

TEST(only_first_n) {
    int arr[] = {1, 2, 3, 4, 5, 6};
    int want[] = {3, 2, 1, 4, 5, 6};
    reverse(arr, 3);
    ASSERT_EQ_INT_ARRAY(arr, want, 6);
}

TEST(large_heap_array) {
    size_t n = 100000;
    int *arr = malloc(n * sizeof(int));
    for (size_t i = 0; i < n; i++) arr[i] = (int)i;
    reverse(arr, n);
    for (size_t i = 0; i < n; i++) ASSERT_EQ_INT(arr[i], (int)(n - 1 - i));
    free(arr);
}
