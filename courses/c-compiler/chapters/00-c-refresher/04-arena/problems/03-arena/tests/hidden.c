#include "forge_test.h"
#include "arena.h"
#include <stdint.h>

TEST(memory_is_zeroed) {
    Arena a;
    arena_init(&a, 256);
    unsigned char *p = arena_alloc(&a, 128, 1);
    for (int i = 0; i < 128; i++) p[i] = 0xAB;
    arena_reset(&a);
    unsigned char *q = arena_alloc(&a, 128, 1);
    for (int i = 0; i < 128; i++) ASSERT_EQ_INT(q[i], 0);
    arena_free(&a);
}

TEST(alignment_of_every_power) {
    Arena a;
    arena_init(&a, 1024);
    size_t aligns[] = {1, 2, 4, 8, 16};
    for (int round = 0; round < 10; round++) {
        for (int i = 0; i < 5; i++) {
            arena_alloc(&a, 1, 1);  /* knock the offset off alignment */
            void *p = arena_alloc(&a, 3, aligns[i]);
            ASSERT_NOT_NULL(p);
            ASSERT_EQ_INT((uintptr_t)p % aligns[i], 0);
        }
    }
    arena_free(&a);
}

TEST(no_overlap) {
    Arena a;
    arena_init(&a, 1000);
    unsigned char *prev_end = a.base;
    for (int i = 1; i < 30; i++) {
        unsigned char *p = arena_alloc(&a, (size_t)i, 4);
        ASSERT_NOT_NULL(p);
        ASSERT_TRUE(p >= prev_end);
        prev_end = p + i;
    }
    ASSERT_TRUE(prev_end <= a.base + a.cap);
    arena_free(&a);
}

TEST(exact_fit) {
    Arena a;
    arena_init(&a, 32);
    ASSERT_NOT_NULL(arena_alloc(&a, 32, 16));
    ASSERT_EQ_INT(a.used, 32);
    ASSERT_NULL(arena_alloc(&a, 1, 1));
    ASSERT_EQ_INT(a.used, 32);
    arena_free(&a);
}

TEST(alignment_pushes_past_end) {
    Arena a;
    arena_init(&a, 20);
    arena_alloc(&a, 17, 1);
    ASSERT_NULL(arena_alloc(&a, 1, 16)); /* would start at 32 > 20 */
    ASSERT_EQ_INT(a.used, 17);
    arena_free(&a);
}

TEST(reset_reuses_memory) {
    Arena a;
    arena_init(&a, 64);
    void *first = arena_alloc(&a, 10, 8);
    arena_alloc(&a, 10, 8);
    arena_reset(&a);
    ASSERT_EQ_INT(a.used, 0);
    ASSERT_TRUE(arena_alloc(&a, 10, 8) == first);
    arena_free(&a);
    ASSERT_NULL(a.base);
    ASSERT_EQ_INT(a.cap, 0);
}

TEST(strndup_empty_and_full) {
    Arena a;
    arena_init(&a, 16);
    ASSERT_EQ_STR(arena_strndup(&a, "xyz", 0), "");
    ASSERT_EQ_STR(arena_strndup(&a, "hello", 5), "hello");
    ASSERT_NULL(arena_strndup(&a, "0123456789", 10)); /* 1 + 6 used, 11 more won't fit in 16 */
    arena_free(&a);
}
