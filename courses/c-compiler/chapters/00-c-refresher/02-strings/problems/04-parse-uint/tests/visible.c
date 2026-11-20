#include "forge_test.h"
#include "parse_uint.h"

TEST(example_1_number_then_operator) {
    const char *s = "123+4", *end = 0;
    ASSERT_EQ_INT(parse_uint(s, &end), 123);
    ASSERT_EQ_STR(end, "+4");
}

TEST(example_2_not_a_number) {
    const char *s = "x1", *end = 0;
    ASSERT_EQ_INT(parse_uint(s, &end), -1);
    ASSERT_TRUE(end == s);
}
