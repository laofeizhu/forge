#ifndef VEC_H
#define VEC_H
#include <stddef.h>

typedef struct {
    int *data;
    size_t len;
    size_t cap;
} IntVec;

void vec_push(IntVec *v, int x);
int vec_pop(IntVec *v);
void vec_free(IntVec *v);
#endif
