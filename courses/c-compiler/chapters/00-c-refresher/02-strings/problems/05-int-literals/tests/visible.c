#include "forge_test.h"
#include "int_literal.h"

TEST(example_1_hex) {
    unsigned long v = 0;
    ASSERT_EQ_INT(parse_int_literal("0x1F)", &v), 4);
    ASSERT_EQ_INT(v, 31);
}

TEST(example_2_octal) {
    unsigned long v = 0;
    ASSERT_EQ_INT(parse_int_literal("017", &v), 3);
    ASSERT_EQ_INT(v, 15);
    ASSERT_EQ_INT(parse_int_literal("019", &v), 0);
}
