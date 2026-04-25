import { describe, it, expect } from 'vitest'
import { runC } from '../evaluator'

describe('C evaluator — hello world (printf %d)', () => {
  const SRC = `
int main() {
    int x = 5;
    int y = x + 3;
    printf("%d\\n", y);
    return 0;
}
`
  const snapshots = runC(SRC)
  const last = snapshots[snapshots.length - 1]

  it('produces no error', () => {
    expect(last.error).toBeNull()
  })

  it('prints 8 (5 + 3)', () => {
    expect(last.output).toEqual(['8'])
  })

  it('opens main frame and binds x and y', () => {
    expect(last.stack[0].name).toBe('Globals')
    const main = last.stack.find((f) => f.name === 'main')
    expect(main).toBeTruthy()
    const x = main!.bindings.find((b) => b.name === 'x' && !b.retired)
    const y = main!.bindings.find((b) => b.name === 'y' && !b.retired)
    expect(x?.value).toEqual({ kind: 'int', v: 5 })
    expect(y?.value).toEqual({ kind: 'int', v: 8 })
  })
})

describe('C evaluator — control flow (if/while/for)', () => {
  const SRC = `
int main() {
    int sum = 0;
    int i = 1;
    while (i <= 5) {
        sum = sum + i;
        i = i + 1;
    }
    if (sum == 15) {
        printf("ok\\n");
    } else {
        printf("bad\\n");
    }
    return 0;
}
`
  const snapshots = runC(SRC)
  const last = snapshots[snapshots.length - 1]

  it('sums 1..5 = 15 and prints "ok"', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['ok'])
    const main = last.stack.find((f) => f.name === 'main')!
    const sum = main.bindings.find((b) => b.name === 'sum' && !b.retired)
    expect(sum?.value).toEqual({ kind: 'int', v: 15 })
  })
})

describe('C evaluator — function call frames', () => {
  const SRC = `
int square(int n) {
    return n * n;
}

int main() {
    int x = square(4);
    printf("%d\\n", x);
    return 0;
}
`
  const snapshots = runC(SRC)
  const last = snapshots[snapshots.length - 1]

  it('prints 16', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['16'])
  })

  it('keeps both Globals + main + retired square frame', () => {
    expect(last.stack.map((f) => f.name)).toContain('square')
    const sq = last.stack.find((f) => f.name === 'square')!
    expect(sq.retired).toBe(true)
    expect(sq.returnValue).toEqual({ kind: 'int', v: 16 })
  })
})

describe('C evaluator — for loop', () => {
  const SRC = `
int main() {
    int total = 0;
    for (int i = 0; i < 4; i = i + 1) {
        total = total + i;
    }
    printf("%d\\n", total);
    return 0;
}
`
  const snapshots = runC(SRC)
  const last = snapshots[snapshots.length - 1]

  it('sums 0+1+2+3 = 6', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['6'])
  })
})

describe('C evaluator — char + printf %c', () => {
  const SRC = `
int main() {
    char c = 'A';
    printf("%c\\n", c);
    printf("%c\\n", c + 1);
    return 0;
}
`
  const snapshots = runC(SRC)
  const last = snapshots[snapshots.length - 1]

  it('prints A then B', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['A', 'B'])
  })
})

describe('C evaluator — division by zero error surfaces', () => {
  const SRC = `
int main() {
    int x = 1;
    int y = 0;
    int z = x / y;
    return z;
}
`
  const snapshots = runC(SRC)
  const last = snapshots[snapshots.length - 1]

  it('produces a runtime error mentioning "division by zero"', () => {
    expect(last.error).toMatch(/division by zero/)
  })
})
