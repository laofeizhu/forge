#include "mcc.h"

// 1.3-02 / 1.3-05: append the whole program for `int main() { return value; }` to out.
void emit_program(StrBuf *out, long value) {
    sb_append(out, "    .globl _main\n");
    sb_append(out, "    .p2align 2\n");
    sb_append(out, "_main:\n");
    if (value <= 65535) {
        sb_appendf(out, "    mov x0, #%ld\n", value);
    } else {
        unsigned long v = (unsigned long)value;
        sb_appendf(out, "    movz x0, #%lu\n", v & 0xFFFF);
        for (int k = 1; k < 4; k++) {
            unsigned long chunk = (v >> (16 * k)) & 0xFFFF;
            if (chunk) sb_appendf(out, "    movk x0, #%lu, lsl #%d\n", chunk, 16 * k);
        }
    }
    sb_append(out, "    ret\n");
}
