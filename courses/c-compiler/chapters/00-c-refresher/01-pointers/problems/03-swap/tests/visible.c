#include "forge_test.h"
#include "swap.h"

TEST(example_1_two_variables) {
    int x = 1, y = 2;
    swap(&x, &y);
    ASSERT_EQ_INT(x, 2);
    ASSERT_EQ_INT(y, 1);
}

TEST(example_2_array_elements) {
    int arr[3] = {7, 8, 9};
    swap(&arr[0], &arr[2]);
    int want[3] = {9, 8, 7};
    ASSERT_EQ_INT_ARRAY(arr, want, 3);
}
