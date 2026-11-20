/* forge_test.h — tiny test harness for forge C courses.
 *
 *   #include "forge_test.h"
 *   TEST(adds_small_numbers) { ASSERT_EQ_INT(add(2, 3), 5); }
 *
 * Each TEST runs in its own forked process, so a crash or infinite loop in one
 * test does not hide the results of the others. Results are printed by the
 * harness as one JSON object per line; anything your code prints is captured
 * and shown next to the test that printed it.
 */
#ifndef FORGE_TEST_H
#define FORGE_TEST_H

#include <stddef.h>
#include <stdio.h>
#include <string.h>

typedef void (*forge_test_fn)(void);

void forge_register(const char *name, forge_test_fn fn, const char *file, int line);
void forge_fail(const char *file, int line, const char *expr, const char *expected, const char *got);
void forge_assert_str(const char *file, int line, const char *expr, const char *got, const char *expected);
void forge_assert_int_array(const char *file, int line, const char *expr,
                            const int *got, const int *expected, size_t n);

#define TEST(name)                                                              \
    static void forge_test_##name(void);                                        \
    __attribute__((constructor)) static void forge_reg_##name(void) {           \
        forge_register(#name, forge_test_##name, __FILE__, __LINE__);           \
    }                                                                           \
    static void forge_test_##name(void)

#define ASSERT_TRUE(cond)                                                       \
    do { if (!(cond)) forge_fail(__FILE__, __LINE__, #cond, "true", "false"); } while (0)

#define ASSERT_FALSE(cond)                                                      \
    do { if ((cond)) forge_fail(__FILE__, __LINE__, "!(" #cond ")", "false", "true"); } while (0)

#define ASSERT_EQ_INT(actual, expected)                                         \
    do {                                                                        \
        long long forge_a_ = (long long)(actual);                               \
        long long forge_e_ = (long long)(expected);                             \
        if (forge_a_ != forge_e_) {                                             \
            char forge_eb_[32], forge_gb_[32];                                  \
            snprintf(forge_eb_, sizeof forge_eb_, "%lld", forge_e_);            \
            snprintf(forge_gb_, sizeof forge_gb_, "%lld", forge_a_);            \
            forge_fail(__FILE__, __LINE__, #actual, forge_eb_, forge_gb_);      \
        }                                                                       \
    } while (0)

#define ASSERT_EQ_STR(actual, expected)                                         \
    forge_assert_str(__FILE__, __LINE__, #actual, (actual), (expected))

#define ASSERT_EQ_INT_ARRAY(actual, expected, n)                                \
    forge_assert_int_array(__FILE__, __LINE__, #actual, (actual), (expected), (n))

#define ASSERT_NULL(p)                                                          \
    do { if ((p) != NULL) forge_fail(__FILE__, __LINE__, #p, "NULL", "non-NULL pointer"); } while (0)

#define ASSERT_NOT_NULL(p)                                                      \
    do { if ((p) == NULL) forge_fail(__FILE__, __LINE__, #p, "non-NULL pointer", "NULL"); } while (0)

#endif
