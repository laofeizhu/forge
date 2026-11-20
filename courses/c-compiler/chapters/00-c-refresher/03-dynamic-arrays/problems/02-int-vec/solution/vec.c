#include "vec.h"
#include <stdlib.h>

void vec_push(IntVec *v, int x) {
    if (v->len == v->cap) {
        v->cap = v->cap ? v->cap * 2 : 8;
        v->data = realloc(v->data, v->cap * sizeof *v->data);
    }
    v->data[v->len++] = x;
}

int vec_pop(IntVec *v) {
    return v->data[--v->len];
}

void vec_free(IntVec *v) {
    free(v->data);
    *v = (IntVec){0};
}
