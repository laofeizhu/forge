// main.c: the compiler driver. Provided by the course: read it, you don't need to change it.
//
//   mcc input.c -o output.s     compile input.c, write assembly to output.s
//   mcc input.c -o -            ... or print it to the terminal
#include "mcc.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Read a whole file into a malloc'd, '\0'-terminated buffer. The CALLER owns it and must free() it.
static char *read_file(const char *path) {
    FILE *f = fopen(path, "rb");
    if (f == NULL) return NULL;
    StrBuf sb = {0};
    char buf[4096];
    size_t n;
    while ((n = fread(buf, 1, sizeof buf, f)) > 0) sb_append_n(&sb, buf, n);
    fclose(f);
    if (sb.data == NULL) sb_append(&sb, "");  // empty file: still hand back a valid "" buffer
    return sb.data;                           // ownership moves to the caller; sb itself is dropped
}

int main(int argc, char **argv) {
    const char *in = NULL, *out = NULL;
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-o") == 0 && i + 1 < argc) out = argv[++i];
        else in = argv[i];
    }
    if (in == NULL || out == NULL) {
        fprintf(stderr, "usage: mcc input.c -o output.s\n");
        return 2;
    }
    char *src = read_file(in);
    if (src == NULL) {
        fprintf(stderr, "mcc: cannot read %s\n", in);
        return 2;
    }

    StrBuf asm_text = {0};
    int err = compile(src, &asm_text);
    free(src);
    if (err) {
        sb_free(&asm_text);
        return 1;
    }

    FILE *f = strcmp(out, "-") == 0 ? stdout : fopen(out, "w");
    if (f == NULL) {
        fprintf(stderr, "mcc: cannot write %s\n", out);
        sb_free(&asm_text);
        return 2;
    }
    fputs(sb_cstr(&asm_text), f);
    if (f != stdout) fclose(f);
    sb_free(&asm_text);
    return 0;
}
