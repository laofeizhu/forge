#include "forge_test.h"
#include "my_strlen.h"
#include <stdlib.h>

TEST(stops_at_first_nul) { ASSERT_EQ_INT(my_strlen("ab\0cd"), 2); }
TEST(whitespace_counts) { ASSERT_EQ_INT(my_strlen(" \t\n"), 3); }

TEST(long_heap_string) {
    char *s = malloc(10001);
    for (int i = 0; i < 10000; i++) s[i] = 'x';
    s[10000] = '\0';
    ASSERT_EQ_INT(my_strlen(s), 10000);
    free(s);
}
