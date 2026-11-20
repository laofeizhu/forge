#include "arena.h"
#include <stdlib.h>
#include <string.h>

static size_t align_up(size_t x, size_t align) {
    return (x + align - 1) & ~(align - 1);
}

int arena_init(Arena *a, size_t cap) {
    a->base = malloc(cap);
    a->cap = a->base ? cap : 0;
    a->used = 0;
    return a->base != NULL;
}

void *arena_alloc(Arena *a, size_t size, size_t align) {
    size_t start = align_up(a->used, align);
    if (start > a->cap || size > a->cap - start) return NULL;
    void *p = a->base + start;
    memset(p, 0, size);
    a->used = start + size;
    return p;
}

char *arena_strndup(Arena *a, const char *s, size_t n) {
    char *p = arena_alloc(a, n + 1, 1);
    if (p) memcpy(p, s, n);
    return p;
}

void arena_reset(Arena *a) {
    a->used = 0;
}

void arena_free(Arena *a) {
    free(a->base);
    *a = (Arena){0};
}
