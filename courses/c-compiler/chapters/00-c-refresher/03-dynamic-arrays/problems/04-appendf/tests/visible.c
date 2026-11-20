#include "forge_test.h"
#include "strbuf.h"

TEST(example_1_number) {
    StrBuf sb = {0};
    sb_appendf(&sb, "  mov x0, #%d\n", 42);
    ASSERT_EQ_STR(sb_cstr(&sb), "  mov x0, #42\n");
    sb_free(&sb);
}

TEST(example_2_two_calls) {
    StrBuf sb = {0};
    sb_appendf(&sb, "%s:", "_main");
    sb_appendf(&sb, "%s", "\n");
    ASSERT_EQ_STR(sb_cstr(&sb), "_main:\n");
    sb_free(&sb);
}
