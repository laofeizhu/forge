#include "forge_test.h"
#include "parse_uint.h"

TEST(zero) {
    const char *end;
    ASSERT_EQ_INT(parse_uint("0", &end), 0);
    ASSERT_EQ_STR(end, "");
}

TEST(leading_zeros) {
    const char *end;
    ASSERT_EQ_INT(parse_uint("007;", &end), 7);
    ASSERT_EQ_STR(end, ";");
}

TEST(empty_string) {
    const char *s = "", *end = 0;
    ASSERT_EQ_INT(parse_uint(s, &end), -1);
    ASSERT_TRUE(end == s);
}

TEST(minus_is_not_a_digit) {
    const char *s = "-5", *end = 0;
    ASSERT_EQ_INT(parse_uint(s, &end), -1);
    ASSERT_TRUE(end == s);
}

TEST(eighteen_digits) {
    const char *end;
    ASSERT_EQ_INT(parse_uint("123456789012345678 ", &end), 123456789012345678L);
    ASSERT_EQ_STR(end, " ");
}

TEST(chained_calls) {
    const char *p = "10,20", *end;
    ASSERT_EQ_INT(parse_uint(p, &end), 10);
    ASSERT_EQ_INT(parse_uint(end + 1, &end), 20);
    ASSERT_EQ_STR(end, "");
}
