#include "forge_test.h"
#include "arena.h"

TEST(example_1_alignment) {
    Arena a;
    ASSERT_EQ_INT(arena_init(&a, 64), 1);
    char *c = arena_alloc(&a, 1, 1);
    ASSERT_NOT_NULL(c);
    ASSERT_EQ_INT(a.used, 1);
    long *l = arena_alloc(&a, 8, 8);
    ASSERT_TRUE((unsigned char *)l == a.base + 8);
    ASSERT_EQ_INT(a.used, 16);
    arena_free(&a);
}

TEST(example_2_full_and_strndup) {
    Arena a;
    arena_init(&a, 64);
    arena_alloc(&a, 1, 1);
    arena_alloc(&a, 8, 8);
    ASSERT_NULL(arena_alloc(&a, 100, 8));
    ASSERT_EQ_INT(a.used, 16);
    ASSERT_EQ_STR(arena_strndup(&a, "main(void)", 4), "main");
    arena_free(&a);
}
