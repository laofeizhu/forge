#include "forge_test.h"
#include "vec.h"

TEST(free_empty_is_safe) {
    IntVec v = {0};
    vec_free(&v);
    ASSERT_NULL(v.data);
}

TEST(many_pushes_keep_values) {
    IntVec v = {0};
    for (int i = 0; i < 10000; i++) vec_push(&v, i * 3);
    ASSERT_EQ_INT(v.len, 10000);
    ASSERT_EQ_INT(v.cap, 16384);
    for (int i = 0; i < 10000; i++) ASSERT_EQ_INT(v.data[i], i * 3);
    vec_free(&v);
}

TEST(pop_is_lifo) {
    IntVec v = {0};
    vec_push(&v, 1);
    vec_push(&v, 2);
    vec_push(&v, 3);
    ASSERT_EQ_INT(vec_pop(&v), 3);
    ASSERT_EQ_INT(vec_pop(&v), 2);
    vec_push(&v, 4);
    ASSERT_EQ_INT(vec_pop(&v), 4);
    ASSERT_EQ_INT(vec_pop(&v), 1);
    ASSERT_EQ_INT(v.len, 0);
    vec_free(&v);
}

TEST(reuse_after_free) {
    IntVec v = {0};
    vec_push(&v, 5);
    vec_free(&v);
    vec_push(&v, 6);
    ASSERT_EQ_INT(v.len, 1);
    ASSERT_EQ_INT(v.cap, 8);
    ASSERT_EQ_INT(v.data[0], 6);
    vec_free(&v);
}

TEST(exact_boundary_8) {
    IntVec v = {0};
    for (int i = 0; i < 8; i++) vec_push(&v, i);
    ASSERT_EQ_INT(v.cap, 8);
    vec_push(&v, 8);
    ASSERT_EQ_INT(v.cap, 16);
    ASSERT_EQ_INT(v.data[8], 8);
    vec_free(&v);
}
