#include "forge_test.h"
#include "ident.h"

TEST(example_1_predicates) {
    ASSERT_EQ_INT(is_ident_start('_'), 1);
    ASSERT_EQ_INT(is_ident_start('7'), 0);
    ASSERT_EQ_INT(is_ident_char('7'), 1);
    ASSERT_EQ_INT(is_ident_char('+'), 0);
}

TEST(example_2_ident_len) {
    ASSERT_EQ_INT(ident_len("count+1"), 5);
    ASSERT_EQ_INT(ident_len("9lives"), 0);
}
