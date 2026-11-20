#include "forge_test.h"
#include "min_max.h"
#include <limits.h>

TEST(single_element) {
    int arr[] = {5};
    int lo = 0, hi = 0;
    ASSERT_EQ_INT(min_max(arr, 1, &lo, &hi), 1);
    ASSERT_EQ_INT(lo, 5);
    ASSERT_EQ_INT(hi, 5);
}

TEST(all_negative) {
    int arr[] = {-5, -9, -2};
    int lo = 0, hi = 0;
    min_max(arr, 3, &lo, &hi);
    ASSERT_EQ_INT(lo, -9);
    ASSERT_EQ_INT(hi, -2);
}

TEST(extremes) {
    int arr[] = {0, INT_MAX, INT_MIN, 1};
    int lo = 0, hi = 0;
    min_max(arr, 4, &lo, &hi);
    ASSERT_EQ_INT(lo, INT_MIN);
    ASSERT_EQ_INT(hi, INT_MAX);
}
