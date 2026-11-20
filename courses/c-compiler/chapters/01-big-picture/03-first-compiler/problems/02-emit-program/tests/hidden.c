#include "forge_test.h"
#include "mcc.h"

TEST(value_0) {
    StrBuf out = {0};
    emit_program(&out, 0);
    ASSERT_EQ_STR(sb_cstr(&out), "    .globl _main\n    .p2align 2\n_main:\n    mov x0, #0\n    ret\n");
    sb_free(&out);
}

TEST(value_65535) {
    StrBuf out = {0};
    emit_program(&out, 65535);
    ASSERT_EQ_STR(sb_cstr(&out), "    .globl _main\n    .p2align 2\n_main:\n    mov x0, #65535\n    ret\n");
    sb_free(&out);
}

TEST(appends_after_existing_text) {
    StrBuf out = {0};
    sb_append(&out, "// header\n");
    emit_program(&out, 1);
    ASSERT_EQ_STR(sb_cstr(&out), "// header\n    .globl _main\n    .p2align 2\n_main:\n    mov x0, #1\n    ret\n");
    sb_free(&out);
}
