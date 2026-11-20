#include "forge_test.h"
#include "min_max.h"

TEST(example_1) {
    int arr[] = {3, -1, 7, 2};
    int lo = 0, hi = 0;
    ASSERT_EQ_INT(min_max(arr, 4, &lo, &hi), 1);
    ASSERT_EQ_INT(lo, -1);
    ASSERT_EQ_INT(hi, 7);
}

TEST(example_2_empty) {
    int lo = 111, hi = 222;
    ASSERT_EQ_INT(min_max(NULL, 0, &lo, &hi), 0);
    ASSERT_EQ_INT(lo, 111);
    ASSERT_EQ_INT(hi, 222);
}
