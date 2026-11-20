#ifndef STRBUF_H
#define STRBUF_H
#include <stddef.h>

typedef struct {
    char *data;
    size_t len;
    size_t cap;
} StrBuf;

void sb_append_n(StrBuf *sb, const char *s, size_t n);
void sb_append(StrBuf *sb, const char *s);
void sb_append_char(StrBuf *sb, char c);
void sb_appendf(StrBuf *sb, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
const char *sb_cstr(StrBuf *sb);
void sb_free(StrBuf *sb);
#endif
