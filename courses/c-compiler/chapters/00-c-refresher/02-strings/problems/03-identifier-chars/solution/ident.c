#include "ident.h"

int is_ident_start(char c) {
    return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || c == '_';
}

int is_ident_char(char c) {
    return is_ident_start(c) || (c >= '0' && c <= '9');
}

size_t ident_len(const char *s) {
    if (!is_ident_start(*s)) return 0;
    size_t n = 1;
    while (is_ident_char(s[n])) n++;
    return n;
}
