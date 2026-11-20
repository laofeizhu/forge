/* forge_test.c — runner for forge_test.h. Do not edit; forge links it in. */
#define _DARWIN_C_SOURCE
#define _DEFAULT_SOURCE
#include "forge_test.h"

#include <signal.h>
#include <stdlib.h>
#include <sys/wait.h>
#include <unistd.h>

typedef struct {
    const char *name;
    const char *file;
    int line;
    forge_test_fn fn;
} ForgeTest;

static ForgeTest forge_tests[512];
static int forge_ntests;
static int forge_fail_fd = -1;

void forge_register(const char *name, forge_test_fn fn, const char *file, int line) {
    if (forge_ntests < 512) {
        forge_tests[forge_ntests++] = (ForgeTest){name, file, line, fn};
    }
}

static void json_str(FILE *f, const char *s, size_t limit) {
    fputc('"', f);
    size_t n = 0;
    for (; s && *s && n < limit; s++, n++) {
        unsigned char c = (unsigned char)*s;
        switch (c) {
        case '"': fputs("\\\"", f); break;
        case '\\': fputs("\\\\", f); break;
        case '\n': fputs("\\n", f); break;
        case '\r': fputs("\\r", f); break;
        case '\t': fputs("\\t", f); break;
        default:
            if (c < 0x20) fprintf(f, "\\u%04x", c);
            else fputc(c, f);
        }
    }
    if (s && *s) fputs("\\n... (truncated)", f);
    fputc('"', f);
}

void forge_fail(const char *file, int line, const char *expr, const char *expected, const char *got) {
    fflush(stdout);
    fflush(stderr);
    if (forge_fail_fd >= 0) {
        FILE *f = fdopen(forge_fail_fd, "w");
        const char *base = strrchr(file, '/');
        fprintf(f, "\"file\":");
        json_str(f, base ? base + 1 : file, 256);
        fprintf(f, ",\"line\":%d,\"expr\":", line);
        json_str(f, expr, 1024);
        fprintf(f, ",\"expected\":");
        json_str(f, expected, 4096);
        fprintf(f, ",\"got\":");
        json_str(f, got, 4096);
        fflush(f);
    }
    _exit(1);
}

static void quote(char *buf, size_t cap, const char *s) {
    if (!s) { snprintf(buf, cap, "NULL"); return; }
    snprintf(buf, cap, "\"%s\"", s);
}

void forge_assert_str(const char *file, int line, const char *expr, const char *got, const char *expected) {
    if (got && expected && strcmp(got, expected) == 0) return;
    if (!got && !expected) return;
    char eb[4096], gb[4096];
    quote(eb, sizeof eb, expected);
    quote(gb, sizeof gb, got);
    forge_fail(file, line, expr, eb, gb);
}

static void fmt_array(char *buf, size_t cap, const int *a, size_t n) {
    size_t off = 0;
    off += snprintf(buf + off, cap - off, "[");
    for (size_t i = 0; i < n && off < cap - 16; i++) {
        off += snprintf(buf + off, cap - off, "%s%d", i ? ", " : "", a[i]);
    }
    snprintf(buf + off, cap - off, "]");
}

void forge_assert_int_array(const char *file, int line, const char *expr,
                            const int *got, const int *expected, size_t n) {
    if (memcmp(got, expected, n * sizeof(int)) == 0) return;
    char eb[4096], gb[4096];
    fmt_array(eb, sizeof eb, expected, n);
    fmt_array(gb, sizeof gb, got, n);
    forge_fail(file, line, expr, eb, gb);
}

static char *slurp(FILE *f) {
    fseek(f, 0, SEEK_END);
    long n = ftell(f);
    rewind(f);
    char *buf = malloc((size_t)n + 1);
    size_t got = fread(buf, 1, (size_t)n, f);
    buf[got] = '\0';
    return buf;
}

static int is_hidden(const ForgeTest *t) { return strstr(t->file, "hidden") != NULL; }

static int cmp_tests(const void *a, const void *b) {
    const ForgeTest *x = a, *y = b;
    if (is_hidden(x) != is_hidden(y)) return is_hidden(x) - is_hidden(y);
    return x->line - y->line;
}

int main(void) {
    qsort(forge_tests, (size_t)forge_ntests, sizeof(ForgeTest), cmp_tests);
    int timeout = 2;
    const char *t = getenv("FORGE_TIMEOUT");
    if (t) timeout = atoi(t);
    int failed = 0;

    for (int i = 0; i < forge_ntests; i++) {
        ForgeTest *test = &forge_tests[i];
        int pipefd[2];
        if (pipe(pipefd) != 0) return 2;
        FILE *out = tmpfile();
        fflush(stdout);

        pid_t pid = fork();
        if (pid == 0) {
            close(pipefd[0]);
            forge_fail_fd = pipefd[1];
            dup2(fileno(out), STDOUT_FILENO);
            dup2(fileno(out), STDERR_FILENO);
            alarm((unsigned)timeout);
            test->fn();
            fflush(stdout);
            _exit(0);
        }
        close(pipefd[1]);
        char info[16384];
        size_t ilen = 0;
        ssize_t r;
        while ((r = read(pipefd[0], info + ilen, sizeof info - 1 - ilen)) > 0) ilen += (size_t)r;
        info[ilen] = '\0';
        close(pipefd[0]);
        int status = 0;
        waitpid(pid, &status, 0);
        char *output = slurp(out);
        fclose(out);

        const char *verdict;
        if (WIFSIGNALED(status)) {
            verdict = WTERMSIG(status) == SIGALRM ? "timeout" : "crash";
        } else if (WEXITSTATUS(status) == 0) {
            verdict = "pass";
        } else {
            verdict = ilen ? "fail" : "crash";
        }
        if (strcmp(verdict, "pass") != 0) failed++;

        printf("{\"name\":");
        json_str(stdout, test->name, 256);
        printf(",\"hidden\":%s,\"status\":\"%s\"", is_hidden(test) ? "true" : "false", verdict);
        if (WIFSIGNALED(status)) printf(",\"signal\":\"%s\"", strsignal(WTERMSIG(status)));
        else printf(",\"exit_code\":%d", WEXITSTATUS(status));
        if (ilen) printf(",%s", info);
        printf(",\"output\":");
        json_str(stdout, output, 8192);
        printf("}\n");
        fflush(stdout);
        free(output);
    }
    return failed ? 1 : 0;
}
