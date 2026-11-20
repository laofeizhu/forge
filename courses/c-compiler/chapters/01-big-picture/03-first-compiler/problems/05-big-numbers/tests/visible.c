#include "forge_test.h"
#include "mcc.h"

#define HEAD "    .globl _main\n    .p2align 2\n_main:\n"

TEST(small_stays_mov) {
    StrBuf out = {0};
    emit_program(&out, 42);
    ASSERT_EQ_STR(sb_cstr(&out), HEAD "    mov x0, #42\n    ret\n");
    sb_free(&out);
}

TEST(seventy_thousand_uses_movz_movk) {
    StrBuf out = {0};
    emit_program(&out, 70000);
    ASSERT_EQ_STR(sb_cstr(&out), HEAD "    movz x0, #4464\n    movk x0, #1, lsl #16\n    ret\n");
    sb_free(&out);
}
