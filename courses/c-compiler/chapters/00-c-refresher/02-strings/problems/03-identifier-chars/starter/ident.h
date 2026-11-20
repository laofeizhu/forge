#ifndef IDENT_H
#define IDENT_H
#include <stddef.h>
int is_ident_start(char c);
int is_ident_char(char c);
size_t ident_len(const char *s);
#endif
