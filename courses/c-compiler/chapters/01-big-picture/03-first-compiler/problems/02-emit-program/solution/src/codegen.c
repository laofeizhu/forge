#include "mcc.h"

// 1.3-02: append the whole program for `int main() { return value; }` to out.
void emit_program(StrBuf *out, long value) {
    sb_append(out, "    .globl _main\n");
    sb_append(out, "    .p2align 2\n");
    sb_append(out, "_main:\n");
    sb_appendf(out, "    mov x0, #%ld\n", value);
    sb_append(out, "    ret\n");
}
