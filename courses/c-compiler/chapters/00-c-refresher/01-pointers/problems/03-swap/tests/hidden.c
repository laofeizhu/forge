#include "forge_test.h"
#include "swap.h"
#include <limits.h>

TEST(same_pointer_is_noop) {
    int x = 42;
    swap(&x, &x);
    ASSERT_EQ_INT(x, 42);
}

TEST(extreme_values) {
    int x = INT_MIN, y = INT_MAX;
    swap(&x, &y);
    ASSERT_EQ_INT(x, INT_MAX);
    ASSERT_EQ_INT(y, INT_MIN);
}

TEST(swap_twice_restores) {
    int x = -3, y = 5;
    swap(&x, &y);
    swap(&x, &y);
    ASSERT_EQ_INT(x, -3);
    ASSERT_EQ_INT(y, 5);
}
