// The 7 COMP110 QZ00 practice problems. Source:
// https://comp110-26s.github.io/resources/practice/sp26/qz00/qz00_memory_diagrams.html
// Each problem's `source` is verbatim Python; `title` and `prompt` are what the
// course site shows alongside the diagram.

export type Problem = {
  id: string
  title: string
  prompt: string
  source: string
}

export const QZ00_PROBLEMS: Problem[] = [
  {
    id: 'basic_howdy',
    title: 'Basic 00 — Howdy Partner',
    prompt:
      'Two variable declarations, then a reassignment. Trace how Globals changes.',
    source: `b: str = "Partner"
a: str = "Howdy "
a = a + b
print(a)
`,
  },
  {
    id: 'basic_mardi',
    title: 'Basic 01 — Mardi Gras',
    prompt:
      'String indexing + reassignment. `c` never changes after line 3 — `a` does. Which value prints?',
    source: `a: str = "Mardi"
b: str = "Gras"
c: str = a[0] + a[len(b)]
a = "yay!"
print(c)
`,
  },
  {
    id: 'basic_ab',
    title: 'Basic 02 — a / b build-up',
    prompt:
      'Build `b` from `a`, print a combination, then rebuild `a` using len(b). Two printed lines.',
    source: `a: str = "a"
b: str = a + "b" + "b"
print(b + a)
a = a + str(len(b))
print(a)
`,
  },
  {
    id: 'basic_age',
    title: 'Basic 03 — Age / Year',
    prompt:
      'Arithmetic with typed declarations. No reassignment — every binding stays active.',
    source: `age: int = 20
year: int = 2024
older_age: int = age + 10
later_year: int = year + 10
print("In " + str(later_year) + " you'll be " + str(older_age))
`,
  },
  {
    id: 'func_import',
    title: 'Functions — Big / Bigger / Biggest (with assignment)',
    prompt:
      'Nested calls combined with local variable assignment inside main(). Watch main\'s frame: `a` gets reassigned twice.',
    source: `def big_func(num: int) -> int:
    a: int = num + 2
    return a

def bigger_func(num: int) -> int:
    a: int = big_func(num=num) * 2
    return a

def biggest_func(num: int) -> int:
    a: int = bigger_func(num=num) ** 2
    return a

def main() -> None:
    a: int = 110
    a = biggest_func(num=a)
    print("Wow! " + str(a) + " is a big number!")

main()
`,
  },
  {
    id: 'calzones',
    title: 'Calzones',
    prompt:
      'Predict the final Output. Calzones are $7 each, strombolis are $8 each, plus a $3 service fee.',
    source: `def total_price(calzones: int, strombolis: int) -> int:
    """Returns the total price for the order of food, including a service fee of $3."""
    return calzones_price(calzones=calzones) + strombolis_price(strombolis=strombolis) + 3

def calzones_price(calzones: int) -> int:
    """Returns the price of the given number of calzones."""
    return 7 * calzones

def strombolis_price(strombolis: int) -> int:
    """Returns the price of the given number of strombolis."""
    return 8 * strombolis

print(total_price(calzones=4, strombolis=2))
`,
  },
  {
    id: 'circle',
    title: 'Circumference & Area',
    prompt:
      'Step through main(). Predict the two printed lines — note the order of the calls.',
    source: `"""Functions of a circle..."""

def main() -> None:
    """Entrypoint of Program"""
    print(circumference(radius=1.0))
    print(area(radius=1.0))
    return None

def area(radius: float) -> float:
    """Calculate area of a circle"""
    return 3.14 * radius ** 2

def circumference(radius: float) -> float:
    """Calculate circumference"""
    return 2 * 3.14 * radius

main()
`,
  },
  {
    id: 'big_func',
    title: 'Big / Bigger / Biggest',
    prompt:
      'Three nested function calls. What does biggest_func(num=110) evaluate to?',
    source: `def big_func(a: int) -> int:
    return a + 2

def bigger_func(b: int) -> int:
    return big_func(a=b) * 2

def biggest_func(num: int) -> int:
    return bigger_func(b=num) ** 2

def main() -> None:
    print(str(biggest_func(num=110)) + " is a big number!")

main()
`,
  },
  {
    id: 'division',
    title: 'Division (unreachable code)',
    prompt:
      'The print inside division() is unreachable — the return fires first. Output shows the same value twice?',
    source: `def division(x: int, y: int) -> float:
    return y / x
    print(y % x)

print(division(y=64, x=16))

print(int(64/16))
`,
  },
  {
    id: 'start_end',
    title: 'Start & End',
    prompt:
      'Only the second call is printed. What string lands in Output?',
    source: `def start_end(word: str) -> str:
    return word[0] + word[len(word)-1]

start_end(word="kitkat")
print(start_end(word="skittles"))
`,
  },
  {
    id: 'cookies',
    title: 'Cookies per Student',
    prompt:
      'Trace give_cookies(total_cookies=11, num_students=2). Predict both printed lines.',
    source: `def give_cookies(total_cookies: int, num_students: int) -> int:
    print("Extra cookies: " + str(total_cookies % num_students))
    return int((total_cookies - (total_cookies % num_students))/2)

print("Each student gets " + str(give_cookies(total_cookies=11, num_students=2)) + " cookies")
`,
  },
  {
    id: 'mystery',
    title: 'Mystery Word',
    prompt:
      'Three helper functions composed together. Extract one character from "mystery" — which one?',
    source: `def get_starting_point(word: str) -> int:
    return int(len(word) / 3)

def shift_position(index: int) -> int:
    return index - 1

def extract_character(word: str, index: int) -> str:
    return word[index]

def main(word: str) -> None:
    print("The hidden character is: " + extract_character(word=word, index=shift_position(index=get_starting_point(word=word))))

main(word="mystery")
`,
  },
  {
    id: 'list_reference',
    title: 'Lists — reference aliasing via create/increase',
    prompt:
      "Watch how `list_2 = list_1` shares the same heap list; then `list_1 = create()` rebinds list_1 to a fresh list. After increase(list_1, 2), list_1 prints [2, 3, 4] but list_2 still shows [0, 1, 2].",
    source: `def create() -> list[int]:
    """An obnoxious way to make a list."""
    list_1: list[int] = []
    i: int = 0
    while i < 3:
        list_1.append(i)
        i += 1
    return list_1


def increase(a_list: list[int], x: int) -> None:
    """Lets pump it up!"""
    i: int = 0
    while i < len(a_list):
        a_list[i] += x
        i += 1
    return None


def main() -> None:
    """Entrypoint of the program."""
    list_1: list[int] = create()
    list_2: list[int] = list_1
    list_1 = create()
    increase(list_1, 2)
    print(list_1)
    print(list_2)


main()
`,
  },
  {
    id: 'list_basics',
    title: 'Lists — append + while loop',
    prompt:
      'Build a list from 0 to 4 with a while loop and watch each append land as a new slot on the heap list.',
    source: `numbers: list[int] = []
i: int = 0
while i < 5:
    numbers.append(i * 2)
    i += 1
print(numbers)
`,
  },
  {
    id: 'knight_castle',
    title: 'OOP — Knight & Castle',
    prompt:
      'Two classes with __init__ and __str__. Watch the heap gain a Knight instance, a Castle instance, and see drawbridge_up get struck through when close() reassigns it.',
    source: `class Knight:
    """A medieval Knight."""
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f"Sir {self.name}"

class Castle:
    """A medieval castle with a drawbridge for crossing a surrounding moat and a guarding knight."""
    guard: Knight
    drawbridge_up: bool

    def __init__(self, guard: Knight, bridge_up: bool):
        self.guard = guard
        self.drawbridge_up = bridge_up

    def __str__(self) -> str:
        if self.drawbridge_up:
            return f"Guarded by {self.guard} and closed to outsiders!"
        else:
            return f"Guarded by {self.guard} but open to all!"

    def open(self) -> None:
        if self.drawbridge_up:
            print("Let down the bridge!")
            self.drawbridge_up = False
        else:
            print("Already open!")

    def close(self) -> None:
        if not self.drawbridge_up:
            print("Pull up the bridge!")
            self.drawbridge_up = True
        else:
            print("Already closed!")


lancelot: Knight = Knight("Lancelot")
my_castle: Castle = Castle(lancelot, False)
print(my_castle)
my_castle.close()
print(my_castle)
`,
  },
  {
    id: 'simple_class',
    title: 'OOP — Point (warm-up)',
    prompt:
      'A minimal class. __init__ sets x and y; move() reassigns both. Watch the Point instance attributes get struck through on reassignment.',
    source: `class Point:
    x: int
    y: int

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def move(self, dx: int, dy: int) -> None:
        self.x = self.x + dx
        self.y = self.y + dy

    def __str__(self) -> str:
        return f"({self.x}, {self.y})"

p: Point = Point(3, 4)
print(p)
p.move(dx=1, dy=-2)
print(p)
`,
  },
  {
    id: 'conditional',
    title: 'Conditionals — grade',
    prompt:
      'if / elif / else with comparisons. Step through the truthy branch selection.',
    source: `def grade(score: int) -> str:
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    else:
        return "F"

print(grade(score=85))
`,
  },
  {
    id: 'blank',
    title: 'Write your own',
    prompt:
      'Type any Python code that uses v0 features (def, return, function calls, variable assignment, print, len, int, str, float, arithmetic, string indexing). Press Run and step through.',
    source: `def double(n: int) -> int:
    return n * 2

x: int = 7
y: int = double(n=x)
print(y)
`,
  },
]
