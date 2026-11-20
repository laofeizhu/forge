#include "forge_test.h"
#include "int_literal.h"

TEST(decimal) {
    unsigned long v = 0;
    ASSERT_EQ_INT(parse_int_literal("42;", &v), 2);
    ASSERT_EQ_INT(v, 42);
}

TEST(plain_zero) {
    unsigned long v = 99;
    ASSERT_EQ_INT(parse_int_literal("0", &v), 1);
    ASSERT_EQ_INT(v, 0);
}

TEST(upper_hex) {
    unsigned long v = 0;
    ASSERT_EQ_INT(parse_int_literal("0XABCdef ", &v), 8);
    ASSERT_EQ_INT(v, 0xABCdef);
}

TEST(bare_0x_is_invalid) {
    unsigned long v = 7;
    ASSERT_EQ_INT(parse_int_literal("0x", &v), 0);
    ASSERT_EQ_INT(parse_int_literal("0x;", &v), 0);
    ASSERT_EQ_INT(v, 7);
}

TEST(suffix_is_invalid) {
    unsigned long v = 7;
    ASSERT_EQ_INT(parse_int_literal("12abc", &v), 0);
    ASSERT_EQ_INT(parse_int_literal("0x1g", &v), 0);
    ASSERT_EQ_INT(parse_int_literal("10_", &v), 0);
    ASSERT_EQ_INT(v, 7);
}

TEST(not_a_number) {
    unsigned long v = 7;
    ASSERT_EQ_INT(parse_int_literal("x12", &v), 0);
    ASSERT_EQ_INT(parse_int_literal("", &v), 0);
}

TEST(big_hex) {
    unsigned long v = 0;
    ASSERT_EQ_INT(parse_int_literal("0xffffffffffffffff", &v), 18);
    ASSERT_TRUE(v == 0xffffffffffffffffUL);
}
