#include "forge_test.h"
#include "strbuf.h"
#include <string.h>

TEST(mixed_with_append) {
    StrBuf sb = {0};
    sb_append(&sb, "a");
    sb_appendf(&sb, "%c%ld%s", 'b', -7L, "c");
    sb_append_char(&sb, 'd');
    ASSERT_EQ_STR(sb_cstr(&sb), "ab-7cd");
    ASSERT_EQ_INT(sb.len, 6);
    sb_free(&sb);
}

TEST(empty_format) {
    StrBuf sb = {0};
    sb_appendf(&sb, "%s", "");
    ASSERT_EQ_STR(sb_cstr(&sb), "");
    ASSERT_EQ_INT(sb.len, 0);
    sb_free(&sb);
}

TEST(very_long_output) {
    static char big[10001];
    memset(big, 'z', 10000);
    StrBuf sb = {0};
    sb_appendf(&sb, "[%s]", big);
    ASSERT_EQ_INT(sb.len, 10002);
    ASSERT_EQ_INT(sb.data[0], '[');
    ASSERT_EQ_INT(sb.data[10001], ']');
    ASSERT_EQ_INT(sb.data[10002], 0);
    sb_free(&sb);
}

TEST(many_small_calls) {
    StrBuf sb = {0};
    for (int i = 0; i < 1000; i++) sb_appendf(&sb, "%d,", i % 10);
    ASSERT_EQ_INT(sb.len, 2000);
    ASSERT_EQ_INT(strncmp(sb_cstr(&sb), "0,1,2,3,", 8), 0);
    sb_free(&sb);
}
