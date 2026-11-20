#include "forge_test.h"
#include "strbuf.h"

TEST(example_1_build_a_line) {
    StrBuf sb = {0};
    sb_append(&sb, "mov x0, ");
    sb_append(&sb, "#42");
    sb_append_char(&sb, '\n');
    ASSERT_EQ_STR(sb_cstr(&sb), "mov x0, #42\n");
    ASSERT_EQ_INT(sb.len, 12);
    sb_free(&sb);
}

TEST(example_2_append_n) {
    StrBuf sb = {0};
    sb_append_n(&sb, "return;", 6);
    ASSERT_EQ_STR(sb_cstr(&sb), "return");
    ASSERT_EQ_INT(sb.len, 6);
    sb_free(&sb);
}
