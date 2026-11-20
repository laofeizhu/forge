#include "forge_test.h"
#include "ident.h"

TEST(range_edges) {
    ASSERT_EQ_INT(is_ident_start('a'), 1);
    ASSERT_EQ_INT(is_ident_start('z'), 1);
    ASSERT_EQ_INT(is_ident_start('A'), 1);
    ASSERT_EQ_INT(is_ident_start('Z'), 1);
    ASSERT_EQ_INT(is_ident_start('@'), 0);  /* just before 'A' */
    ASSERT_EQ_INT(is_ident_start('['), 0);  /* just after 'Z' */
    ASSERT_EQ_INT(is_ident_start('`'), 0);  /* just before 'a' */
    ASSERT_EQ_INT(is_ident_start('{'), 0);  /* just after 'z' */
    ASSERT_EQ_INT(is_ident_char('0'), 1);
    ASSERT_EQ_INT(is_ident_char('9'), 1);
    ASSERT_EQ_INT(is_ident_char('/'), 0);
    ASSERT_EQ_INT(is_ident_char(':'), 0);
}

TEST(returns_exactly_one) {
    ASSERT_EQ_INT(is_ident_start('q'), 1);
    ASSERT_EQ_INT(is_ident_char('5'), 1);
}

TEST(whitespace_and_nul) {
    ASSERT_EQ_INT(is_ident_char(' '), 0);
    ASSERT_EQ_INT(is_ident_char('\0'), 0);
    ASSERT_EQ_INT(ident_len(""), 0);
}

TEST(ident_len_cases) {
    ASSERT_EQ_INT(ident_len("_"), 1);
    ASSERT_EQ_INT(ident_len("x2_y3 = 1"), 5);
    ASSERT_EQ_INT(ident_len("int main"), 3);
    ASSERT_EQ_INT(ident_len("(x)"), 0);
}
