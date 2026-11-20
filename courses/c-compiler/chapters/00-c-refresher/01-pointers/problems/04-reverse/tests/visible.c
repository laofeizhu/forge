#include "forge_test.h"
#include "reverse.h"

TEST(example_1_odd_length) {
    int arr[] = {1, 2, 3, 4, 5};
    int want[] = {5, 4, 3, 2, 1};
    reverse(arr, 5);
    ASSERT_EQ_INT_ARRAY(arr, want, 5);
}

TEST(example_2_even_length) {
    int arr[] = {1, 2};
    int want[] = {2, 1};
    reverse(arr, 2);
    ASSERT_EQ_INT_ARRAY(arr, want, 2);
}
