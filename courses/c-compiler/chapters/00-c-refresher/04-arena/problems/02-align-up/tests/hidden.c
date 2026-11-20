#include "forge_test.h"
#include "align.h"

TEST(align_one_is_identity) {
    for (size_t x = 0; x < 50; x++) ASSERT_EQ_INT(align_up(x, 1), x);
}

TEST(all_small_values) {
    size_t aligns[] = {2, 4, 8, 16, 4096};
    for (int i = 0; i < 5; i++) {
        size_t a = aligns[i];
        for (size_t x = 0; x < 3 * a; x++) {
            size_t want = ((x + a - 1) / a) * a;
            ASSERT_EQ_INT(align_up(x, a), want);
        }
    }
}

TEST(pow2_table) {
    ASSERT_EQ_INT(is_pow2(1), 1);
    ASSERT_EQ_INT(is_pow2(2), 1);
    ASSERT_EQ_INT(is_pow2(3), 0);
    ASSERT_EQ_INT(is_pow2(1024), 1);
    ASSERT_EQ_INT(is_pow2(1023), 0);
    ASSERT_EQ_INT(is_pow2((size_t)1 << 63), 1);
    ASSERT_EQ_INT(is_pow2(((size_t)1 << 63) + 1), 0);
}
