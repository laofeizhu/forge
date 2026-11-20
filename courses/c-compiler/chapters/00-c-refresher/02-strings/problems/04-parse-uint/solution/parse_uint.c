#include "parse_uint.h"

long parse_uint(const char *s, const char **end) {
    const char *p = s;
    long n = 0;
    while (*p >= '0' && *p <= '9') {
        n = n * 10 + (*p - '0');
        p++;
    }
    *end = p;
    return p == s ? -1 : n;
}
