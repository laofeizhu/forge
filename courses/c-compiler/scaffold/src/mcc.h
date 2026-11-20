// mcc.h: every interface in your compiler, in one place. The course fixes these signatures
// (tests call them directly); how you implement them is up to you.
#ifndef MCC_H
#define MCC_H
#include <stddef.h>

// ---- strbuf.c: the string builder from 0.3 (reference version, swap in yours if you like) ----
typedef struct {
    char *data;  // always '\0'-terminated once anything was appended
    size_t len;  // chars, not counting the '\0'
    size_t cap;  // bytes allocated
} StrBuf;

void sb_append_n(StrBuf *sb, const char *s, size_t n);
void sb_append(StrBuf *sb, const char *s);
void sb_append_char(StrBuf *sb, char c);
void sb_appendf(StrBuf *sb, const char *fmt, ...) __attribute__((format(printf, 2, 3)));
const char *sb_cstr(StrBuf *sb);
void sb_free(StrBuf *sb);

// ---- codegen.c (1.3-02) ----
// Append the complete assembly program for `int main() { return value; }` to out.
void emit_program(StrBuf *out, long value);

// ---- token.c (1.3-03) ----
// Skip whitespace at *p, then return where the next token starts and set *len to its length.
// A token is a word [A-Za-z0-9_]+ or a single other char. At the end of input: returns a pointer to
// the '\0' with *len == 0 and leaves *p there. The token is a slice of the source: nothing is copied.
const char *next_token(const char **p, size_t *len);

// ---- compile.c (1.3-04) ----
// Compile mini-C source text, appending arm64 assembly to out.
// Returns 0 on success. On error: prints "error: <message>\n" to stderr and returns 1.
int compile(const char *src, StrBuf *out);

#endif
