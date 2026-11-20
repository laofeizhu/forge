#include "forge_test.h"
#include "mcc.h"
#include <stdio.h>

// Print the next token's slice into a buffer so it can be compared as a string.
static const char *tok(const char **p) {
    static char buf[64];
    size_t n = 99;
    const char *t = next_token(p, &n);
    snprintf(buf, sizeof buf, "%.*s", (int)n, t);
    return buf;
}

TEST(example_return_42) {
    const char *p = "int main(){return 42;}";
    ASSERT_EQ_STR(tok(&p), "int");
    ASSERT_EQ_STR(tok(&p), "main");
    ASSERT_EQ_STR(tok(&p), "(");
    ASSERT_EQ_STR(tok(&p), ")");
    ASSERT_EQ_STR(tok(&p), "{");
    ASSERT_EQ_STR(tok(&p), "return");
    ASSERT_EQ_STR(tok(&p), "42");
    ASSERT_EQ_STR(tok(&p), ";");
    ASSERT_EQ_STR(tok(&p), "}");
    ASSERT_EQ_STR(tok(&p), "");
    ASSERT_EQ_INT(*p, '\0');
}
