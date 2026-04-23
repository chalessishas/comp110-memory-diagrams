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
]
