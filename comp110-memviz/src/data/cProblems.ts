// C teaching programs. Aimed at intro-CS students seeing memory diagrams
// for the first time. Kept short (<25 lines) so the diagram fits on screen.
//
// Scope matches the current C interpreter: int / char / arithmetic / printf
// (%d %c %s with string-literal-only %s) / if-else / while / for / functions.
// Pointers / malloc / arrays come in the next iteration.

export type CProblem = {
  id: string
  title: string
  group?: string
  prompt: string
  source: string
}

export const C_PROBLEMS: CProblem[] = [
  {
    id: 'c-hello',
    group: 'Basics',
    title: 'Hello + arithmetic',
    prompt: 'Declare two ints, compute their sum, print it. Watch x and y appear in main\'s stack frame.',
    source: `int main() {
    int x = 5;
    int y = x + 3;
    printf("x = %d\\n", x);
    printf("y = %d\\n", y);
    return 0;
}
`,
  },
  {
    id: 'c-reassign',
    group: 'Basics',
    title: 'Reassignment (strikethrough)',
    prompt: 'Reassigning a variable retires its old binding. Notice the strikethrough on x = 5 once x = 10 takes over.',
    source: `int main() {
    int x = 5;
    printf("before: %d\\n", x);
    x = 10;
    printf("after: %d\\n", x);
    return 0;
}
`,
  },
  {
    id: 'c-if',
    group: 'Control flow',
    title: 'if / else',
    prompt: 'Branch on a comparison. Try changing 7 to a smaller number and re-running.',
    source: `int main() {
    int n = 7;
    if (n % 2 == 0) {
        printf("%d is even\\n", n);
    } else {
        printf("%d is odd\\n", n);
    }
    return 0;
}
`,
  },
  {
    id: 'c-while',
    group: 'Control flow',
    title: 'while loop — sum 1..5',
    prompt: 'Accumulate 1+2+3+4+5 in a while loop. Step through to watch sum and i grow.',
    source: `int main() {
    int sum = 0;
    int i = 1;
    while (i <= 5) {
        sum = sum + i;
        i = i + 1;
    }
    printf("sum = %d\\n", sum);
    return 0;
}
`,
  },
  {
    id: 'c-for',
    group: 'Control flow',
    title: 'for loop — countdown',
    prompt: 'A for loop prints 5 down to 1. The init binding for i lives only inside main\'s frame.',
    source: `int main() {
    for (int i = 5; i > 0; i = i - 1) {
        printf("%d\\n", i);
    }
    printf("blast off!\\n");
    return 0;
}
`,
  },
  {
    id: 'c-square',
    group: 'Functions',
    title: 'square(n) — single function call',
    prompt: 'Calling square pushes a new stack frame. After return the frame stays visible (struck through) so you can see what happened.',
    source: `int square(int n) {
    int result = n * n;
    return result;
}

int main() {
    int x = square(4);
    printf("4 squared = %d\\n", x);
    return 0;
}
`,
  },
  {
    id: 'c-factorial',
    group: 'Functions',
    title: 'factorial — recursion',
    prompt: 'Recursion stacks one frame per call. After all returns, you see the chain of retired factorial frames.',
    source: `int factorial(int n) {
    if (n <= 1) {
        return 1;
    }
    return n * factorial(n - 1);
}

int main() {
    int r = factorial(4);
    printf("4! = %d\\n", r);
    return 0;
}
`,
  },
  {
    id: 'c-char',
    group: 'Types',
    title: 'char arithmetic — A → Z',
    prompt: 'A char is just a small int. Adding 1 to \\\'A\\\' gives \\\'B\\\'. Watch the value flip between number and letter form.',
    source: `int main() {
    char c = 'A';
    int i = 0;
    while (i < 5) {
        printf("%c\\n", c + i);
        i = i + 1;
    }
    return 0;
}
`,
  },
]
