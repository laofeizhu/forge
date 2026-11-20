#include "forge_test.h"
#include "mcc.h"

TEST(example_value_7) {
    StrBuf out = {0};
    emit_program(&out, 7);
    ASSERT_EQ_STR(sb_cstr(&out), "    .globl _main\n    .p2align 2\n_main:\n    mov x0, #7\n    ret\n");
    sb_free(&out);
}
