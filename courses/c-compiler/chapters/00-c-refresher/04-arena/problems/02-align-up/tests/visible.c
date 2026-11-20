#include "forge_test.h"
#include "align.h"

TEST(example_1_align_up) {
    ASSERT_EQ_INT(align_up(13, 8), 16);
    ASSERT_EQ_INT(align_up(16, 8), 16);
    ASSERT_EQ_INT(align_up(0, 16), 0);
}

TEST(example_2_is_pow2) {
    ASSERT_EQ_INT(is_pow2(8), 1);
    ASSERT_EQ_INT(is_pow2(12), 0);
    ASSERT_EQ_INT(is_pow2(0), 0);
}
