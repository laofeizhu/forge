# 0.2 Strings & characters

Your lexer's job is to read source text one character at a time. So: what *is* text in C?

## A char is a small number

```c
char c = 'A';      // exactly the same as  char c = 65;
'A' + 1            // == 'B'  (66)
```

The ASCII table puts related characters next to each other, which makes classification arithmetic:

```
'0' '1' ... '9'     48 .. 57      digits are consecutive  → digit value = c - '0'
'A' ... 'Z'         65 .. 90
'a' ... 'z'         97 .. 122
'_'                 95
' ' '\t' '\n'       32, 9, 10
```

So "is `c` a digit?" is just `c >= '0' && c <= '9'`.

## A string is chars followed by a zero

```c
const char *s = "int";
```
```
 s
 ↓
┌─────┬─────┬─────┬─────┐
│ 'i' │ 'n' │ 't' │ '\0'│      '\0' is the char with value 0
└─────┴─────┴─────┴─────┘
```

There is no length stored anywhere. To find the end you walk until you hit `'\0'`:

```c
const char *p = s;
while (*p != '\0') p++;     // p now points at the terminator
size_t len = p - s;         // subtracting pointers gives a distance in elements
```

## Walking with a cursor

A lexer keeps a pointer to "where I am" and advances it:

```c
const char *cur = "123+x";
long n = 0;
while (*cur >= '0' && *cur <= '9') {
    n = n * 10 + (*cur - '0');   // shift left one decimal place, add the new digit
    cur++;
}
// n == 123, cur points at "+x"
```

`n * 10 + digit` is the core of number parsing. Trace it: 0 → 1 → 12 → 123.

## Slices: pointer + length

Copying every identifier into a fresh string is wasteful. A compiler usually refers to text *inside*
the source with a **slice**: a pointer to the first character plus a length. `"x"` in the example
above is just `(cur, 1)`. You'll see this pattern again in chapter 2.

## Safety net

Reading past the `'\0'` is a classic C bug. Your tests run with AddressSanitizer, which turns it into
a clear `heap-buffer-overflow` report instead of a silent wrong answer.
