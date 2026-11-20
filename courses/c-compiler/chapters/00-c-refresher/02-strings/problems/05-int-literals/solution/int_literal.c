#include "int_literal.h"

static int digit_value(char c) {
    if (c >= '0' && c <= '9') return c - '0';
    if (c >= 'a' && c <= 'f') return c - 'a' + 10;
    if (c >= 'A' && c <= 'F') return c - 'A' + 10;
    return -1;
}

static int is_ident_char(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_' || (c >= '0' && c <= '9');
}

size_t parse_int_literal(const char *s, unsigned long *out) {
    const char *p = s;
    unsigned base = 10;
    if (!(*p >= '0' && *p <= '9')) return 0;
    if (p[0] == '0' && (p[1] == 'x' || p[1] == 'X')) {
        base = 16;
        p += 2;
        if (digit_value(*p) < 0) return 0;
    } else if (p[0] == '0') {
        base = 8;
    }
    unsigned long n = 0;
    for (int d; (d = digit_value(*p)) >= 0 && (unsigned)d < base; p++) {
        n = n * base + (unsigned)d;
    }
    if (is_ident_char(*p)) return 0;
    *out = n;
    return (size_t)(p - s);
}
