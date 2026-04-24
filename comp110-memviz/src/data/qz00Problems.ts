// Auto-generated from COMP110-24S practice memory-diagram problems.
// See https://comp110-24s.github.io/resources/practice/MemDiagrams.html
// Every problem here is verified to parse and run correctly in this
// tool's interpreter (see scripts/audit.test.ts).

export type Problem = {
  id: string
  title: string
  prompt: string
  source: string
  group?: string
}

export const QZ00_PROBLEMS: Problem[] = [
  {
    id: "basic_basic_00",
    title: "Basics: basic-00",
    prompt: "Two string variables plus a reassignment. Watch a get retired when rebound.",
    group: "Basics",
    source: `""" Practice Memory Diagram """

b: str = "Partner"
a: str = "Howdy "
a += b
print(a)\n`,
  },
  {
    id: "basic_basic_01",
    title: "Basics: basic-01",
    prompt: "String indexing + reassignment. c is computed before a changes \u2014 what prints?",
    group: "Basics",
    source: `""" Practice Memory Diagram """

a: str = "Mardi"
b: str = "Gras"
c: str = a[0] + a[len(b)]
a = "yay!"
print(c)\n`,
  },
  {
    id: "basic_basic_02",
    title: "Basics: basic-02",
    prompt: "Build b from a, print combined, then rebuild a using len(b). Two printed lines.",
    group: "Basics",
    source: `""" Practice Memory Diagram """

a: str = "a"
b: str = a + "b" + "b"
print(b + a)
a = a + str(len(b))
print(a)\n`,
  },
  {
    id: "basic_basic_03",
    title: "Basics: basic-03",
    prompt: "Typed declarations + arithmetic + str() casts. No reassignment.",
    group: "Basics",
    source: `""" Practice Memory Diagram """

age: int = 20
year: int = 2024
older_age: int = age + 10
later_year: int = year + 10
print("In " + str(later_year) + " you'll be " + str(older_age))\n`,
  },
  {
    id: "conditionals_conditionals_00",
    title: "Conditionals: conditionals-00",
    prompt: "if with a modulo check. y is conditionally doubled, then shifted by -6. String index follows.",
    group: "Conditionals",
    source: `""" Practice Memory Diagram """

x: str = "Hello"
y: int = len(x)
if y % 4 == 1:
    y *= 2
y -= 6
print(y)
print(x[y])\n`,
  },
  {
    id: "conditionals_conditionals_01",
    title: "Conditionals: conditionals-01",
    prompt: "if/else with string repetition y *= x. Two prints.",
    group: "Conditionals",
    source: `""" Practice Memory Diagram """

x: int = 2
y: str = "yo"
z: str = "2"
if len(y) > 1:
    y *= x
else:
    y = "no"
if x > 0:
    print(z)
print(y)\n`,
  },
  {
    id: "elif_elif_00",
    title: "Conditionals (elif): elif-00",
    prompt: "if / elif / else with comparisons.",
    group: "Conditionals (elif)",
    source: `""" Practice Memory Diagram """

a: int = 2
b: int = 6
if a > b:
    print(a-b)
elif b < 10:
    print(b/a)
else:
    print(a+b)
print(b)\n`,
  },
  {
    id: "while_while_00",
    title: "While loops: while-00",
    prompt: "while + if/elif chain with string accumulation. Predict the final string.",
    group: "While loops",
    source: `""" Practice Memory Diagram """

i: int = 0
s: str = ""

while i < 4:
    if i % 2 == 0:
        s += "h"
    elif i % 3 == 0:
        s += "!"
    else:
        s += "e"
    i += 1
print(s)\n`,
  },
  {
    id: "while_while_01",
    title: "While loops: while-01",
    prompt: "Nested arithmetic in a while body. Watch x, y, z evolve.",
    group: "While loops",
    source: `"""Loops Practice!"""

x: int = 0
y: int = 3
z: str = "1"

while x < y:
    z = z + str(y) + str(x)
    x = x + 1

print(x)
print(y)
print(z)\n`,
  },
  {
    id: "while_while_02",
    title: "While loops: while-02",
    prompt: "Descending while with conditional string prepend/append.",
    group: "While loops",
    source: `""" Practice Memory Diagram """

x: int = 10
result: str = ""

while x >= 0:
    if x % 3 > 0:
        result = result + str(x)
    else:
        result = str(x) + result
    x = x - 1

print(result)\n`,
  },
  {
    id: "functions_func_import_00",
    title: "Functions: func-import-00",
    prompt: "Three nested functions. biggest_func(110) prints a big number via an f-string.",
    group: "Functions",
    source: `def big_func(num: int) -> int:
    a: int = num + 2
    return a

def bigger_func(num: int) -> int:
    a: int = big_func(num) * 2
    return a

def biggest_func(num: int) -> int:
    a: int = bigger_func(num) ** 2
    return a

def main() -> None:
    a: int = 110 
    a = biggest_func(a)
    print(f"Wow! {a} is a big number!")

main()\n`,
  },
  {
    id: "functions_func_import_01",
    title: "Functions: func-import-01",
    prompt: "Compound boolean in an if, followed by a while loop inside the function.",
    group: "Functions",
    source: `def subtraction(x: int) -> int:
    if not x == 10 or x > 8:
        while x > 7: 
            x -= 1
    return x

def to_ten(y: int) -> int:
    while y < 10:
        y += 2
    return y

def main():
    num1: int = 2
    num1 = to_ten(num1)
    num1 = subtraction(num1)
    print(f"The number is {num1}")

main()\n`,
  },
  {
    id: "functions_func_import_02",
    title: "Functions: func-import-02",
    prompt: "A function whose return value is computed but never printed (no output expected).",
    group: "Functions",
    source: `def f(x: str) -> int:
    return len(x) + 1


def g(x: int, y: str) -> int:
    while x > len(y):
        x -= 1
    return x


def main() -> None:
    (g(f("python"), "java"))


main()\n`,
  },
  {
    id: "lists_change_and_check",
    title: "Lists: change-and-check",
    prompt: "List passed by reference; index-assign mutates the caller. append() captures mutated state.",
    group: "Lists",
    source: `"""Practice diagram."""

def change_and_check(x: int, nums: list[int]) -> int:
    """Let's see what happens!"""
    if x < 0:
        return 0
    i: int = 0
    while i < len(nums):
        nums[i] += x
        i += 1
    i = 0
    while i < len(nums):
        if nums[i] == x:
            return 0
        i += 1
    return x - 1


def main() -> None:
    """The entrypoint of this program."""
    num_1: int = 0
    list_1: list[int] = [1, 2, num_1]
    list_1.append(change_and_check(2, list_1))
    list_1.append(change_and_check(3, list_1))

main()\n`,
  },
  {
    id: "lists_lists_00",
    title: "Lists: lists-00",
    prompt: "for over range() and for over a list; both produce side effects via index-assign.",
    group: "Lists",
    source: `def f(x: list[str]) -> str:
    for y in range(0,len(x)):
        x[y] += "x"
    return x[y]

def g(x: list[str]) -> list[str]:
    new_list: list[str] = []
    for z in x:
        new_list.append(str(z))
    return new_list

record: list[str] = ["x", "y"]
print(f(record))
print(g(record))\n`,
  },
  {
    id: "lists_lists_01",
    title: "Lists: lists-01",
    prompt: "while loop + indexed comparison + increment counter. Count matching elements.",
    group: "Lists",
    source: `def check_quiz(responses: list[bool]) -> int:
    answer_key: list[bool] = [True, True, False]
    correct: int = 0
    idx: int = 0
    while idx < len(responses):
        if responses[idx] == answer_key[idx]:
            correct += 1
            idx += 1
        else:
            idx += 1
    return correct

def main() -> None:
    my_quiz: list[bool] = [True, True, True]
    grade: int = check_quiz(my_quiz)
    print(f"{grade} out of 3 questions correct.")


main()\n`,
  },
  {
    id: "lists_references",
    title: "Lists: references",
    prompt: "list_2 = list_1 aliases; then list_1 = create() rebinds. Both print their own state.",
    group: "Lists",
    source: `"""Practice diagram."""

def create() -> list[int]:
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


main()\n`,
  },
  {
    id: "dicts_dicts_00",
    title: "Dictionaries: dicts-00",
    prompt: "for over dict keys with += 1; second function returns a new dict mapping key->str(key).",
    group: "Dictionaries",
    source: `def f(x: dict[str,int]) -> int:
    for y in x:
        x[y] += 1
    return x[y]

def g(x: dict[str,int]) -> dict[str,str]:
    new_dict: dict[str,str] = {}
    for z in x:
        new_dict[z] = str(z)
    return new_dict

record: dict[str, int] = {"x": 20, "y": 40}
print(f(record))
print(g(record))\n`,
  },
  {
    id: "dicts_dicts_01",
    title: "Dictionaries: dicts-01",
    prompt: "if y in x membership test + dict indexing.",
    group: "Dictionaries",
    source: `def mystery(x: dict[str,float], y: str) -> str:
    if y in x:
        return str(x[y])
    else:
        return "not in dictionary"

x = "y"
y = "z"
test: dict[str,float] = {"z": 3.14}
print(mystery(test,y))\n`,
  },
  {
    id: "dicts_lineups",
    title: "Dictionaries: lineups",
    prompt: "Nested dict of lists; indexed write into the inner list. (Source fixed: 24s site had a chained-assign typo.)",
    group: "Dictionaries",
    source: `starting: dict[str, list[str]] = {}
starting["2017"] = ["Berry", "Meeks", "Jackson"]
starting["2023"] = ["Love", "Bacot", "Black"]

print(starting["2017"][2])
print(starting["2023"])
starting["2023"][2] = "Johnson"
print(starting["2023"])\n`,
  },
  {
    id: "recursion_basic_loop",
    title: "Recursion: basic-loop",
    prompt: "Tail-recursive countdown by 2 until x < 3.",
    group: "Recursion",
    source: `def loop(x: int) -> int:
    if x < 3:
        return x
    else:
        return loop(x-2)

print(loop(6))\n`,
  },
  {
    id: "recursion_pow",
    title: "Recursion: pow",
    prompt: "Recursive power-of-2 computation.",
    group: "Recursion",
    source: `def f(n: int) -> int:
    if n == 0:
        return 1
    else:
        return f(n-1) * 2

print(f(3))\n`,
  },
  {
    id: "recursion_silly_loop",
    title: "Recursion: silly-loop",
    prompt: "Recursion that returns no printed value; trace the call stack.",
    group: "Recursion",
    source: `def silly_loop(x: int)-> int:
    if x < 2:
        return x
    else:
        return 2 + silly_loop(x-3) 

silly_loop(10)\n`,
  },
  {
    id: "oop_stadium",
    title: "OOP: stadium",
    prompt: "Class with init + upgrade method touching multiple fields via if/elif/else.",
    group: "OOP",
    source: `class Stadium:
    sponsor: str
    capacity: int
    has_roof: bool
    ticket_price: int

    def __init__(self, s: str, c: int, h: bool):
        self.sponsor = s
        self.capacity = c
        self.has_roof = h
        self.ticket_price = 20
    
    def upgrade(self) -> None:
        if self.capacity > 75000:
            self.has_roof = True
            self.ticket_price += 10
        elif self.sponsor == "FedEx":
            self.capacity += 10000
            self.ticket_price += 5
        else:
            self.capacity += 5000
    
def main() -> None:
    new_arena: Stadium = Stadium("FedEx", 70000, False)
    new_arena.upgrade()
    new_arena.upgrade()
    print(new_arena.ticket_price)


main()\n`,
  },
  {
    id: "oop_tweets",
    title: "OOP: tweets",
    prompt: "Profile class + toggle_privacy using not.",
    group: "OOP",
    source: `class Profile:
    
    handle: str
    followers: int
    is_private: bool
    
    def __init__(self, handle: str):
        self.handle = handle
        self.followers = 0
        self.is_private = False
        
    def send(self, msg: str) ->  None:
        if not self.is_private:
            print(f"@{self.handle} says {msg}")
            
    def toggle_privacy(self) -> None:
        self.is_private = not self.is_private
        
a: Profile = Profile("alyssa")
b: Profile = Profile("tyler")
a.send("Sup")
b.toggle_privacy()
b.send("Heyyy")\n`,
  },
  {
    id: "oop_advanced_board_games",
    title: "OOP \u2014 magic methods: board-games",
    prompt: "Class using in operator and list.pop() inside a while loop.",
    group: "OOP \u2014 magic methods",
    source: `class Games:
    
    set: list[str]
    wishlist: list[str]
    
    def __init__(self, set: list[str], wishlist: list[str]):
        self.set = set
        self.wishlist = wishlist
    
    def __str__(self) -> str:
        return f"My games: {self.set}"
    
    def purchase(self, game):
        if game in self.wishlist:
            idx: int = 0
            while idx < len(self.wishlist):
                if game == self.wishlist[idx]:
                    self.wishlist.pop(idx)
                idx += 1
        self.set.append(game)
        
collection: Games = Games([], ["Uno", "Life"])
collection.purchase("Uno")
collection.purchase("Catan")
print(collection)\n`,
  },
  {
    id: "oop_advanced_playlist",
    title: "OOP \u2014 magic methods: playlist",
    prompt: "__add__ magic method makes p1 + 1 call the class __add__.",
    group: "OOP \u2014 magic methods",
    source: `class Playlist:
    
    name: str
    songs: int
    on_repeat: bool
    
    def __init__(self, name: str, songs: int, repeat: bool):
        self.name = name
        self.songs = songs
        self.on_repeat = repeat
    
    def __add__(self, num_songs: int) -> Playlist:
        return Playlist(self.name + "_copy", self.songs + num_songs, self.on_repeat)
    
    def __str__(self) -> str:
        return f"{self.name}: {self.songs} songs"
    
    def playlist_length(self) -> int:
        total: int = 0
        total = self.songs * 3
        if self.on_repeat:
            total *= 2
        return total
    
p1: Playlist = Playlist("Hits", 9, True)
p2: Playlist = p1 + 1
print(p1)
print(p2.playlist_length())\n`,
  },
  {
    id: "oop_advanced_team",
    title: "OOP \u2014 magic methods: team",
    prompt: "Class that holds a list of players; add_player mutates the field.",
    group: "OOP \u2014 magic methods",
    source: `class Team:
        
    team_name: str
    players: list[str]
        
    def __init__(self, inp_name: str, inp_players: list[str]):
        self.team_name = inp_name
        self.players = inp_players
    
    def add_player(self, player_name: str)-> None:
        self.players.append(player_name)
        
    def __str__(self) -> str:
        info: str = f"{self.team_name}: {self.players}"
        return info
            
teammates: list[str] = ["Alyssa", "Jayden"]
team0: Team = Team("Rockets", teammates)
team1: Team = Team("Wombats", [])
team1.add_player("Chiara")
team1.add_player("Shefali")
print(team1)\n`,
  },
  {
    id: "knight_castle",
    title: "OOP: Knight & Castle",
    prompt: "Two classes with __init__ and __str__. Watch drawbridge_up get struck through on close().",
    group: "OOP",
    source: `class Knight:
    \"\"\"A medieval Knight.\"\"\"
    name: str

    def __init__(self, name: str):
        self.name = name

    def __str__(self) -> str:
        return f\"Sir {self.name}\"

class Castle:
    \"\"\"A medieval castle with a drawbridge.\"\"\"
    guard: Knight
    drawbridge_up: bool

    def __init__(self, guard: Knight, bridge_up: bool):
        self.guard = guard
        self.drawbridge_up = bridge_up

    def __str__(self) -> str:
        if self.drawbridge_up:
            return f\"Guarded by {self.guard} and closed to outsiders!\"
        else:
            return f\"Guarded by {self.guard} but open to all!\"

    def open(self) -> None:
        if self.drawbridge_up:
            print(\"Let down the bridge!\")
            self.drawbridge_up = False
        else:
            print(\"Already open!\")

    def close(self) -> None:
        if not self.drawbridge_up:
            print(\"Pull up the bridge!\")
            self.drawbridge_up = True
        else:
            print(\"Already closed!\")


lancelot: Knight = Knight(\"Lancelot\")
my_castle: Castle = Castle(lancelot, False)
print(my_castle)
my_castle.close()
print(my_castle)
`,
  },
  {
    id: "qz01_count",
    title: "Conditionals: count (return inside if)",
    prompt: "Early return from inside an if skips the unreachable print. What prints?",
    group: "Conditionals",
    source: `def count(x: str) -> str:
    """Practice conditionals."""
    y: int = len(x)
    if y % 4 == 1:
        y = y * 2
    y = y - 6
    print(y)
    return(x[y])
    print(x[y])

count(x="Hello")\n`,
  },
  {
    id: "qz01_xyz",
    title: "Conditionals: xyz (string repetition)",
    prompt: "String gets multiplied by int (repetition). Two separate if-checks.",
    group: "Conditionals",
    source: `def xyz(x: int, y: str) -> str:
    """Practice conditionals."""
    z: str = str(x)
    if len(y) > 1:
        y = y * x
    else:
        y = "no"
    if x > 0:
        print(z)
    return y

xyz(x=2, y="yo")\n`,
  },
  {
    id: "qz01_g",
    title: "Conditionals (elif): g (divide by zero branch)",
    prompt: "elif branch fires when b<10; division of ints yields a float.",
    group: "Conditionals (elif)",
    source: `def g(a: int, b: int) -> None:
    """Practice conditionals."""
    if a > b:
        print(a-b)
    elif b < 10:
        print(b/a)
    else:
        print(a+b)
    print(b)

g(a=2,b=6)\n`,
  },
  {
    id: "qz01_factorial",
    title: "Recursion: factorial(3)",
    prompt: "Recursive factorial with early-exit for n<=1.",
    group: "Recursion",
    source: `"""Recursion practice!"""

def factorial(num: int) -> int:
    """Calculate the factorial of num."""
    if num <= 0:
        return 1
    elif num == 1:
        return 1
    else:
        return num * factorial(num=num - 1)

def main() -> None:
    """The main function."""
    print(factorial(num=3))

main()\n`,
  },
  {
    id: "qz01_palindrome",
    title: "Recursion: is_palindrome",
    prompt: "Recurse on both ends of the string; terminates at midpoint.",
    group: "Recursion",
    source: `"""Recursion practice with palindromes."""

def is_palindrome(word: str, index: int) -> bool:
    """Returns True if word is a palindrome and False otherwise."""
    if index >= int(len(word) / 2):
        return True
    elif word[index] == word[len(word) - (index + 1)]:
        return is_palindrome(word=word, index=index + 1)
    else:
        return False

def main() -> None:
    """The main function."""
    print(is_palindrome(word="noon", index=0))
    print(is_palindrome(word="110", index=0))

main()\n`,
  },
  {
    id: "qz02_count",
    title: "Dictionaries: count occurrences",
    prompt: "Build a dict of occurrence counts using `in` to check key presence.",
    group: "Dictionaries",
    source: `def count(xs: list[int]) -> dict[int, int]:
    counts: dict[int, int] = {}
    for x in xs:
        if x in counts:
            counts[x] += 1
        else:
            counts[x] = 1
    return counts

numbers: list[int] = [1, 1, 0]
print(count(numbers))\n`,
  },
  {
    id: "qz03_dogcat",
    title: "OOP: Dog & Cat (speak / birthday)",
    prompt: "Two class definitions + instances. birthday() increments and returns the new age.",
    group: "OOP",
    source: `class Dog:
   name: str
   age: int
   
   def __init__(self, n: str, a:int):
       self.name = n
       self.age = a
       
   def speak(self) -> None: 
       print(self.name + " says woof!")
       
   def birthday(self) -> int:
       self.age += 1 
       return self.age
       
class Cat:
   name: str
   age: int
   
   def __init__(self, n: str, a:int):
       self.name = n
       self.age = a
       
   def speak(self) -> None: 
       print(self.name + " says meow!")
       
   def birthday(self) -> int:
       self.age += 1 
       return self.age
   
rory: Dog = Dog(n = "Rory", a = 4)
print(rory.birthday())
miso: Cat = Cat("Miso", 2)
miso.speak()\n`,
  },
  {
    id: "qz03_concert",
    title: "OOP: Concert (dict[str,bool] seats + assign_seats)",
    prompt: "Method with nested conditionals; iterates through a list and mutates a dict.",
    group: "OOP",
    source: `class Concert:
    artist: str
    seats: dict[str, bool]

    def __init__(self, a: str, s: dict[str, bool]):
        self.artist = a
        self.seats = s

    def assign_seats(self, wanted_seats: list[str], name: str) -> None:
        for seat in wanted_seats:
            if seat in self.seats:
                available: bool = self.seats[seat]
                if available:
                    print(f"{name} bought seat {seat} to see {self.artist}!")
                    self.seats[seat] = False
                else: 
                   print(f"Seat {seat} is unavailable :(")

lenovo_seats: dict[str, bool] = {"K1": True, "K2": True, "K3": False}
show: Concert = Concert(a = "Travisty", s = lenovo_seats)
show.assign_seats(wanted_seats = ["K2", "K3"], name = "Kay")\n`,
  },
  {
    id: "qz03_linkedlist",
    title: "OOP: messy linked list (Node | None + is None)",
    prompt: "Recursive __str__ via `Node | None` union type and `is None` check.",
    group: "OOP \u2014 magic methods",
    source: `"""A messy linked list..."""

from __future__ import annotations

# Node class definition included for reference!
class Node:
    value: int
    next: Node | None

    def __init__(self, val: int, next: Node | None):
        self.value = val
        self.next = next

    def __str__(self) -> str:
        rest: str
        if self.next is None:
            rest = "None"
        else:
            rest = str(self.next)
        return f"{self.value} -> {rest}"

knight: Node = Node(3, None)
bishop: Node = Node(2, knight)
rook: Node = Node(1, bishop)
print(rook)
castle: Node = Node(0, bishop)
print(castle)\n`,
  },
  {
    id: "blank",
    title: "Write your own",
    prompt: "Type any Python using supported features (def/class/return/call/assign/if/while/for/list/dict/+=/in). Press Run and step through.",
    group: "Custom",
    source: `def double(n: int) -> int:
    return n * 2

x: int = 7
y: int = double(n=x)
print(y)
`,
  },
]
