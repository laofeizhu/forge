#include "strbuf.h"
#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

static void sb_reserve(StrBuf *sb, size_t extra) {
    size_t need = sb->len + extra + 1;
    if (need <= sb->cap) return;
    size_t cap = sb->cap ? sb->cap : 16;
    while (cap < need) cap *= 2;
    sb->data = realloc(sb->data, cap);
    sb->cap = cap;
}

void sb_append_n(StrBuf *sb, const char *s, size_t n) {
    sb_reserve(sb, n);
    memcpy(sb->data + sb->len, s, n);
    sb->len += n;
    sb->data[sb->len] = '\0';
}

void sb_append(StrBuf *sb, const char *s) { sb_append_n(sb, s, strlen(s)); }

void sb_append_char(StrBuf *sb, char c) { sb_append_n(sb, &c, 1); }

void sb_appendf(StrBuf *sb, const char *fmt, ...) {
    va_list ap, ap2;
    va_start(ap, fmt);
    va_copy(ap2, ap);
    int n = vsnprintf(NULL, 0, fmt, ap2);
    va_end(ap2);
    if (n > 0) {
        sb_reserve(sb, (size_t)n);
        vsnprintf(sb->data + sb->len, sb->cap - sb->len, fmt, ap);
        sb->len += (size_t)n;
    }
    va_end(ap);
}

const char *sb_cstr(StrBuf *sb) { return sb->data ? sb->data : ""; }

void sb_free(StrBuf *sb) {
    free(sb->data);
    *sb = (StrBuf){0};
}
