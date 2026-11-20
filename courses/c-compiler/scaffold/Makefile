# Your compiler. `make` builds ./mcc; `make try P=prog.c` compiles prog.c, runs it, shows the exit code.
CFLAGS = -std=c11 -g -O0 -Wall -Wextra -Werror -fsanitize=address,undefined

mcc: src/*.c src/*.h
	cc $(CFLAGS) src/*.c -o mcc

try: mcc
	./mcc $(P) -o /tmp/mcc-out.s && cc /tmp/mcc-out.s -o /tmp/mcc-out && /tmp/mcc-out; echo "exit code: $$?"

clean:
	rm -rf mcc mcc.dSYM
.PHONY: try clean
