#include "forge_test.h"
#include "vec.h"

TEST(example_1_first_pushes) {
    IntVec v = {0};
    vec_push(&v, 10);
    vec_push(&v, 20);
    ASSERT_EQ_INT(v.len, 2);
    ASSERT_EQ_INT(v.cap, 8);
    ASSERT_EQ_INT(v.data[0], 10);
    ASSERT_EQ_INT(v.data[1], 20);
    vec_free(&v);
}

TEST(example_2_grow_pop_free) {
    IntVec v = {0};
    for (int i = 1; i <= 9; i++) vec_push(&v, i);
    ASSERT_EQ_INT(v.cap, 16);
    ASSERT_EQ_INT(vec_pop(&v), 9);
    ASSERT_EQ_INT(v.len, 8);
    vec_free(&v);
    ASSERT_NULL(v.data);
    ASSERT_EQ_INT(v.len, 0);
    ASSERT_EQ_INT(v.cap, 0);
}
