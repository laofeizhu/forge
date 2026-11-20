#include "forge_test.h"
#include "mcc.h"
#include <stdio.h>

static const char *tok(const char **p) {
    static char buf[64];
    size_t n = 99;
    const char *t = next_token(p, &n);
    snprintf(buf, sizeof buf, "%.*s", (int)n, t);
    return buf;
}

TEST(all_whitespace_kinds) {
    const char *p = "\n\t  int\r\n";
    ASSERT_EQ_STR(tok(&p), "int");
    ASSERT_EQ_STR(tok(&p), "");
}

TEST(glued_words_are_one_word) {
    const char *p = "intmain(";
    ASSERT_EQ_STR(tok(&p), "intmain");
    ASSERT_EQ_STR(tok(&p), "(");
}

TEST(word_with_digits) {
    const char *p = "return42;";
    ASSERT_EQ_STR(tok(&p), "return42");
    ASSERT_EQ_STR(tok(&p), ";");
}

TEST(unknown_char_is_one_token) {
    const char *p = "a$b";
    ASSERT_EQ_STR(tok(&p), "a");
    ASSERT_EQ_STR(tok(&p), "$");
    ASSERT_EQ_STR(tok(&p), "b");
}

TEST(empty_and_blank_input) {
    const char *p = "";
    ASSERT_EQ_STR(tok(&p), "");
    const char *q = "   ";
    ASSERT_EQ_STR(tok(&q), "");
    ASSERT_EQ_INT(*q, '\0');
}

TEST(end_is_sticky) {
    const char *src = "x";
    const char *p = src;
    tok(&p);
    for (int i = 0; i < 3; i++) {
        size_t n = 99;
        next_token(&p, &n);
        ASSERT_EQ_INT(n, 0);
        ASSERT_TRUE(p == src + 1);
    }
}

TEST(returns_a_slice_into_the_source) {
    const char *src = "int main";
    const char *p = src;
    size_t n;
    next_token(&p, &n);
    const char *t = next_token(&p, &n);
    ASSERT_TRUE(t == src + 4);
    ASSERT_EQ_INT(n, 4);
    ASSERT_TRUE(p == src + 8);
}
