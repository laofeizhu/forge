#include "forge_test.h"
#include "mcc.h"

#define HEAD "    .globl _main\n    .p2align 2\n_main:\n"

TEST(boundary_65536) {
    StrBuf out = {0};
    emit_program(&out, 65536);
    ASSERT_EQ_STR(sb_cstr(&out), HEAD "    movz x0, #0\n    movk x0, #1, lsl #16\n    ret\n");
    sb_free(&out);
}

TEST(skips_zero_chunks) {
    StrBuf out = {0};
    emit_program(&out, 4294967296L);  // 2^32: only chunk 2 is non-zero
    ASSERT_EQ_STR(sb_cstr(&out), HEAD "    movz x0, #0\n    movk x0, #1, lsl #32\n    ret\n");
    sb_free(&out);
}

TEST(all_four_chunks) {
    StrBuf out = {0};
    emit_program(&out, 9223372036854775807L);
    ASSERT_EQ_STR(sb_cstr(&out), HEAD "    movz x0, #65535\n    movk x0, #65535, lsl #16\n"
                                      "    movk x0, #65535, lsl #32\n    movk x0, #32767, lsl #48\n    ret\n");
    sb_free(&out);
}
