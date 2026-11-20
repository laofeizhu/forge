#include "mcc.h"
#include <ctype.h>
#include <stdio.h>
#include <string.h>

static int is(const char *t, size_t n, const char *want) {
    return n == strlen(want) && strncmp(t, want, n) == 0;
}

static int fail(const char *want, const char *t, size_t n) {
    if (n == 0) fprintf(stderr, "error: expected %s, got end of file\n", want);
    else fprintf(stderr, "error: expected %s, got '%.*s'\n", want, (int)n, t);
    return 1;
}

// 1.3-04: accept exactly `int main() { return N; }` (any whitespace between tokens).
int compile(const char *src, StrBuf *out) {
    const char *p = src, *t;
    size_t n;
    const char *before[] = {"int", "main", "(", ")", "{", "return"};
    for (size_t i = 0; i < sizeof before / sizeof before[0]; i++) {
        t = next_token(&p, &n);
        if (!is(t, n, before[i])) return fail(before[i], t, n);
    }

    t = next_token(&p, &n);
    if (n == 0 || (t[0] == '0' && n > 1)) return fail("a number", t, n);
    long value = 0;
    for (size_t i = 0; i < n; i++) {
        if (!isdigit((unsigned char)t[i])) return fail("a number", t, n);
        value = value * 10 + (t[i] - '0');
        if (value > 65535) return fail("a number <= 65535", t, n);
    }

    const char *after[] = {";", "}"};
    for (size_t i = 0; i < 2; i++) {
        t = next_token(&p, &n);
        if (!is(t, n, after[i])) return fail(after[i], t, n);
    }
    t = next_token(&p, &n);
    if (n != 0) return fail("end of file", t, n);

    emit_program(out, value);
    return 0;
}
