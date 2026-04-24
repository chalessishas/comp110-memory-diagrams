import { describe, it, expect } from 'vitest'
import { run } from '../evaluator'

const CALZONES = `def total_price(calzones: int, strombolis: int) -> int:
    """Returns the total price for the order of food, including a service fee of $3."""
    return calzones_price(calzones=calzones) + strombolis_price(strombolis=strombolis) + 3

def calzones_price(calzones: int) -> int:
    """Returns the price of the given number of calzones."""
    return 7 * calzones

def strombolis_price(strombolis: int) -> int:
    """Returns the price of the given number of strombolis."""
    return 8 * strombolis

print(total_price(calzones=4, strombolis=2))
`

describe('evaluator — calzones QZ00 example', () => {
  const snapshots = run(CALZONES)
  const last = snapshots[snapshots.length - 1]

  it('produces no error', () => {
    expect(last.error).toBeNull()
  })

  it('prints 47 (7*4 + 8*2 + 3)', () => {
    expect(last.output).toEqual(['47'])
  })

  it('creates 3 heap objects for the 3 function defs', () => {
    expect(last.heap).toHaveLength(3)
    const names = last.heap.map((h) => (h.kind === 'function' ? h.name : ''))
    expect(names).toEqual(['total_price', 'calzones_price', 'strombolis_price'])
    expect(last.heap.map((h) => h.id)).toEqual([0, 1, 2])
  })

  it('ends with Globals + 3 retired frames (v0 keeps frames on strike-through)', () => {
    // v0 rule: returned frames stay visible, crossed out. Only Globals is active.
    expect(last.stack).toHaveLength(4)
    expect(last.stack[0].name).toBe('Globals')
    expect(last.stack[0].retired).toBe(false)
    const retiredNames = last.stack.slice(1).map((f) => f.name).sort()
    expect(retiredNames).toEqual(['calzones_price', 'strombolis_price', 'total_price'])
    expect(last.stack.slice(1).every((f) => f.retired)).toBe(true)
  })

  it('globals frame binds each function name to its heap ref', () => {
    const g = last.stack[0].bindings
    const find = (n: string) => g.find((b) => b.name === n && !b.retired)?.value
    expect(find('total_price')).toEqual({ kind: 'ref', id: 0 })
    expect(find('calzones_price')).toEqual({ kind: 'ref', id: 1 })
    expect(find('strombolis_price')).toEqual({ kind: 'ref', id: 2 })
  })

  it('produces enough intermediate snapshots to step through', () => {
    // At minimum: 3 funcDefs + 2 call entries (total_price, calzones_price, strombolis_price) +
    // 3 returns + 1 print + initial + final.
    expect(snapshots.length).toBeGreaterThan(8)
  })
})

describe('evaluator — circle example', () => {
  const src = `def main() -> None:
    print(circumference(radius=1.0))
    print(area(radius=1.0))
    return None

def area(radius: float) -> float:
    return 3.14 * radius ** 2

def circumference(radius: float) -> float:
    return 2 * 3.14 * radius

main()
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('prints circumference then area', () => {
    expect(last.error).toBeNull()
    expect(last.output).toHaveLength(2)
    expect(parseFloat(last.output[0])).toBeCloseTo(6.28, 5)
    expect(parseFloat(last.output[1])).toBeCloseTo(3.14, 5)
  })
})

describe('evaluator — NameError', () => {
  const src = `print(undefined_name)\n`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('surfaces a NameError on the offending line', () => {
    expect(last.error).toContain('NameError')
    expect(last.error).toContain('undefined_name')
    expect(last.currentLine).toBe(1)
  })
})

describe('evaluator — string indexing', () => {
  const src = `def start_end(word: str) -> str:
    return word[0] + word[len(word)-1]

print(start_end(word="skittles"))
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('prints "ss" (first + last of "skittles")', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['ss'])
  })
})

describe('evaluator — variable assignment (Basic 00)', () => {
  const src = `b: str = "Partner"
a: str = "Howdy "
a = a + b
print(a)
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('prints "Howdy Partner"', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['Howdy Partner'])
  })

  it('retires the old `a` binding after reassignment (strike-through rule)', () => {
    const g = last.stack[0].bindings
    const aBindings = g.filter((b) => b.name === 'a')
    expect(aBindings).toHaveLength(2)
    expect(aBindings[0].retired).toBe(true) // old "Howdy "
    expect(aBindings[0].value).toEqual({ kind: 'str', v: 'Howdy ' })
    expect(aBindings[1].retired).toBe(false) // new "Howdy Partner"
    expect(aBindings[1].value).toEqual({ kind: 'str', v: 'Howdy Partner' })
  })
})

describe('evaluator — Basic 01 Mardi Gras', () => {
  const src = `a: str = "Mardi"
b: str = "Gras"
c: str = a[0] + a[len(b)]
a = "yay!"
print(c)
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('prints "Mi" — c is locked in before a is reassigned', () => {
    expect(last.error).toBeNull()
    // c = a[0] + a[len(b)] = "M" + a[4] = "M" + "i" = "Mi"
    expect(last.output).toEqual(['Mi'])
  })
})

describe('evaluator — if/elif/else', () => {
  const src = `def grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    else:
        return "F"

print(grade(score=85))
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('picks the elif branch for 85 and prints "B"', () => {
    expect(last.error).toBeNull()
    expect(last.output).toEqual(['B'])
  })
})

describe('evaluator — class instantiation + __str__ + f-string', () => {
  const src = `class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

p: Point = Point(3, 4)
print(p)
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('creates one class + one instance on the heap', () => {
    expect(last.error).toBeNull()
    const kinds = last.heap.map((h) => h.kind).sort()
    expect(kinds).toEqual(['class', 'instance'])
  })

  it('prints the f-string "(3, 4)"', () => {
    expect(last.output).toEqual(['(3, 4)'])
  })

  it('instance attrs x and y are both active (not retired)', () => {
    const inst = last.heap.find((h) => h.kind === 'instance')
    expect(inst && inst.kind === 'instance').toBe(true)
    if (inst && inst.kind === 'instance') {
      const x = inst.attrs.find((a) => a.name === 'x' && !a.retired)
      const y = inst.attrs.find((a) => a.name === 'y' && !a.retired)
      expect(x?.value).toEqual({ kind: 'int', v: 3 })
      expect(y?.value).toEqual({ kind: 'int', v: 4 })
    }
  })
})

describe('evaluator — attribute reassignment strikes through old value', () => {
  const src = `class Castle:
    open: bool

    def __init__(self, open: bool):
        self.open = open

    def shut(self) -> None:
        self.open = False

c: Castle = Castle(True)
c.shut()
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]
  const inst = last.heap.find((h) => h.kind === 'instance')

  it('has two `open` attr bindings — old True retired, new False active', () => {
    expect(last.error).toBeNull()
    expect(inst && inst.kind === 'instance').toBe(true)
    if (inst && inst.kind === 'instance') {
      const openBindings = inst.attrs.filter((a) => a.name === 'open')
      expect(openBindings).toHaveLength(2)
      expect(openBindings[0].retired).toBe(true)
      expect(openBindings[0].value).toEqual({ kind: 'bool', v: true })
      expect(openBindings[1].retired).toBe(false)
      expect(openBindings[1].value).toEqual({ kind: 'bool', v: false })
    }
  })
})

describe('evaluator — arity mismatch', () => {
  const src = `def f(x: int) -> int:
    return x + 1

print(f())
`
  const snapshots = run(src)
  const last = snapshots[snapshots.length - 1]

  it('raises Function Call Error', () => {
    expect(last.error).toContain('Function Call Error')
  })
})
