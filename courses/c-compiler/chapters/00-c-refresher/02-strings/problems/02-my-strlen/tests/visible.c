#include "forge_test.h"
#include "my_strlen.h"

TEST(example_1_hello) { ASSERT_EQ_INT(my_strlen("hello"), 5); }
TEST(example_2_empty) { ASSERT_EQ_INT(my_strlen(""), 0); }
