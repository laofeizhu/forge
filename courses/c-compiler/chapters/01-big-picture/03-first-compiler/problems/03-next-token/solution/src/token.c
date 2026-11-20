#include "mcc.h"
#include <ctype.h>

static int is_word_char(char c) {
    return isalnum((unsigned char)c) || c == '_';
}

// 1.3-03: see mcc.h for the contract.
const char *next_token(const char **p, size_t *len) {
    const char *s = *p;
    while (*s == ' ' || *s == '\t' || *s == '\n' || *s == '\r') s++;
    const char *start = s;
    if (*s == '\0') {
        // end of input: length 0, stay on the '\0'
    } else if (is_word_char(*s)) {
        while (is_word_char(*s)) s++;
    } else {
        s++;
    }
    *len = (size_t)(s - start);
    *p = s;
    return start;
}
