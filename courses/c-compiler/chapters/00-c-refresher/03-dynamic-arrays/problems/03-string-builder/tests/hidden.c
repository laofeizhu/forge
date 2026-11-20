#include "forge_test.h"
#include "strbuf.h"

TEST(empty_is_empty_string) {
    StrBuf sb = {0};
    ASSERT_EQ_STR(sb_cstr(&sb), "");
    sb_free(&sb);
    ASSERT_NULL(sb.data);
    ASSERT_EQ_INT(sb.cap, 0);
}

TEST(append_empty_string) {
    StrBuf sb = {0};
    sb_append(&sb, "");
    ASSERT_EQ_STR(sb_cstr(&sb), "");
    ASSERT_EQ_INT(sb.len, 0);
    sb_free(&sb);
}

TEST(always_terminated) {
    StrBuf sb = {0};
    for (int i = 0; i < 100; i++) {
        sb_append_char(&sb, (char)('a' + i % 26));
        ASSERT_EQ_INT(sb.data[sb.len], 0);
        ASSERT_TRUE(sb.cap >= sb.len + 1);
    }
    sb_free(&sb);
}

TEST(one_megabyte_of_chars) {
    StrBuf sb = {0};
    for (int i = 0; i < 1 << 20; i++) sb_append_char(&sb, 'x');
    ASSERT_EQ_INT(sb.len, 1 << 20);
    ASSERT_TRUE(sb.cap < (2u << 21));
    sb_free(&sb);
}

TEST(big_single_append) {
    static char big[5000];
    for (int i = 0; i < 4999; i++) big[i] = 'y';
    StrBuf sb = {0};
    sb_append(&sb, "a");
    sb_append(&sb, big);
    ASSERT_EQ_INT(sb.len, 5000);
    ASSERT_EQ_INT(sb.data[0], 'a');
    ASSERT_EQ_INT(sb.data[4999], 'y');
    sb_free(&sb);
}

TEST(append_n_with_embedded_text) {
    StrBuf sb = {0};
    const char *src = "int main(void)";
    sb_append_n(&sb, src + 4, 4);
    ASSERT_EQ_STR(sb_cstr(&sb), "main");
    sb_free(&sb);
}
