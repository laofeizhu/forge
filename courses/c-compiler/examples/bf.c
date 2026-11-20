// Brainfuck interpreter in mini-C: program on stdin, terminated by '!' (33); its input follows.
int putchar(int c);
int getchar();

int prog[30000];
int tape[30000];
int match[30000];
int stack[1000];

int main() {
    int n = 0;
    int c = getchar();
    while (c != -1 && c != 33) {
        if (c == 43 || c == 45 || c == 60 || c == 62 || c == 46 || c == 44 || c == 91 || c == 93) {
            prog[n] = c;
            n = n + 1;
        }
        c = getchar();
    }
    int sp = 0;
    for (int i = 0; i < n; i = i + 1) {          // precompute matching brackets
        if (prog[i] == 91) { stack[sp] = i; sp = sp + 1; }
        if (prog[i] == 93) {
            if (sp == 0) return 1;
            sp = sp - 1;
            match[i] = stack[sp];
            match[stack[sp]] = i;
        }
    }
    if (sp != 0) return 1;
    int pc = 0;
    int p = 0;
    while (pc < n) {
        int op = prog[pc];
        if (op == 43) tape[p] = (tape[p] + 1) % 256;
        else if (op == 45) tape[p] = (tape[p] + 255) % 256;
        else if (op == 62) p = p + 1;
        else if (op == 60) p = p - 1;
        else if (op == 46) putchar(tape[p]);
        else if (op == 44) { c = getchar(); if (c == -1) c = 0; tape[p] = c; }
        else if (op == 91) { if (tape[p] == 0) pc = match[pc]; }
        else if (op == 93) { if (tape[p] != 0) pc = match[pc]; }
        pc = pc + 1;
    }
    return 0;
}
