#ifndef ARENA_H
#define ARENA_H
#include <stddef.h>

typedef struct {
    unsigned char *base;
    size_t cap;
    size_t used;
} Arena;

int arena_init(Arena *a, size_t cap);
void *arena_alloc(Arena *a, size_t size, size_t align);
char *arena_strndup(Arena *a, const char *s, size_t n);
void arena_reset(Arena *a);
void arena_free(Arena *a);
#endif
