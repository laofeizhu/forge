#include "arena.h"
#include <stdlib.h>
#include <string.h>

int arena_init(Arena *a, size_t cap) {
    // TODO
    (void)a;
    (void)cap;
    return 0;
}

void *arena_alloc(Arena *a, size_t size, size_t align) {
    // TODO
    (void)a;
    (void)size;
    (void)align;
    return NULL;
}

char *arena_strndup(Arena *a, const char *s, size_t n) {
    // TODO
    (void)a;
    (void)s;
    (void)n;
    return NULL;
}

void arena_reset(Arena *a) {
    // TODO
    (void)a;
}

void arena_free(Arena *a) {
    // TODO
    (void)a;
}
