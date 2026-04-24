# COMP110 26S Memory Diagram Source Index

Last scanned: 2026-04-24  
Root source: https://comp110-26s.github.io/

This index defines the official source surface for `comp110-memviz`. The scope is
larger than quiz-specific memory diagram practice pages: the 26S site also teaches
and exercises memory/environment diagrams through lesson pages, topic pages,
general practice pages, and slide PDFs.

## Canonical Rules

| Source | URL | Role |
| --- | --- | --- |
| Memory Diagram Rules v0 | https://comp110-26s.github.io/static/slides/memory_diagrams_v0.pdf | Canonical stack/heap/output rules for function definitions, calls, returns, name resolution, arithmetic, and built-ins. |

## Primary Practice Pages

These pages contain code blocks students are explicitly asked to trace as memory
diagrams. They should be treated as the first source set for runnable examples
and regression tests.

| Source | URL | Notes |
| --- | --- | --- |
| QZ00 memory diagram practice | https://comp110-26s.github.io/resources/practice/sp26/qz00/qz00_memory_diagrams.html | 7 code blocks; function calls, RA/RV, arithmetic, string indexing. |
| QZ01 memory diagrams | https://comp110-26s.github.io/resources/practice/sp26/qz01/qz01_memory_diagrams.html | 5 code blocks; conditionals and recursion. |
| QZ02 memory diagram practice | https://comp110-26s.github.io/resources/practice/sp26/qz02/qz02_memory_diagrams.html | 8 code blocks; lists, dictionaries, loops, references. Includes syntax variants the current parser does not fully accept. |
| QZ03 memory diagram practice | https://comp110-26s.github.io/resources/practice/sp26/qz03/qz03_memory_diagrams.html | 4 code blocks; classes, magic methods, linked structures. Official HTML includes manual line numbers and newer syntax that needs normalization/parser support. |

## Practice Solution Assets

These are official visual answer keys. They are not executable source by
themselves, but they are important for visual/semantic comparison.

| Page | Assets |
| --- | --- |
| QZ00 | `calzones_mem_diag.jpg`, `circumference_area_mem_diag.jpg`, `big_func.png`, `division.png`, `start_end.png`, `cookies.png`, `mystery_word.png` under `https://comp110-26s.github.io/static/practice/qz00_practice/` |
| QZ01 | `conditionals-sol-00.png`, `conditionals-sol-01.png`, `elif-sol.png` under `https://comp110-26s.github.io/resources/practice/sp26/qz01/`; `factorial.png`, `palindrome.png` under `https://comp110-26s.github.io/static/practice/qz01_practice/` |
| QZ02 | `refs.png`, `change-and-check.png`, `record-sol.png`, `mystery-dict-sol.png`, `lineup-sol.png` under `https://comp110-26s.github.io/static/practice/qz02_practice/` |
| QZ03 | `dog_cat.png`, `concert.png` under `https://comp110-26s.github.io/static/practice/qz03_practice/`; `castle_soln.png`, `linked_list_soln.png` under `https://comp110-26s.github.io/static/practice/qz04_practice/` even though they are linked from the QZ03 page. |

## General Practice Pages With Memory-Diagram Content

These pages are not named `*_memory_diagrams.html`, but they still contain
memory diagram or RA/RV tracing content and should be indexed for coverage.

| Source | URL | Notes |
| --- | --- | --- |
| QZ00 general practice | https://comp110-26s.github.io/resources/practice/sp26/qz00/qz00_practice.html | Includes RA/return-value conceptual questions and code tracing. |
| QZ01 general practice | https://comp110-26s.github.io/resources/practice/sp26/qz01/qz01_practice.html | Contains conditionals/recursion prompts that explicitly recommend partial memory diagrams. |
| Quiz expectations | https://comp110-26s.github.io/resources/quiz-expectations.html | Names environment/memory diagram questions as an expected quiz format. |

## Lesson And Topic Pages

These are instructional sources that establish vocabulary and examples outside
quiz practice. They should inform UI labels, explanation text, and future parser
coverage.

| Source | URL | Notes |
| --- | --- | --- |
| Variables lesson | https://comp110-26s.github.io/lessons/variables.html | Introduces variables as memory bindings; includes memory/environment diagram examples and images. |
| while loops lesson | https://comp110-26s.github.io/lessons/while_loops.html | Includes loop tracing examples and environment-diagram screenshots. |
| Recursion lesson | https://comp110-26s.github.io/lessons/recursion.html | Explains recursion through function-call frames/stack overflow language. |
| Environment Diagrams topic | https://comp110-26s.github.io/topics/pages/environments.html | Dedicated stack/heap environment diagram page with classes, linked list, and recursion practice images. |
| Recursion overview topic | https://comp110-26s.github.io/topics/pages/recursion.html | Secondary recursion reference that reinforces tracing concepts. |
| Linked List Utils exercise | https://comp110-26s.github.io/exercises/linked_list_utils.html | Linked-list exercise that intersects with recursive/environment diagram coverage. |

## Lesson/Topic Visual Assets

| Page | Assets |
| --- | --- |
| Variables lesson | `ls-vars-diagram.png`, `ls-vars-example.png`, `ls-vars-update.png` under `https://comp110-26s.github.io/static/lessons/variables/` |
| while loops lesson | `ls-while.png`, `ls-reverse.png` under `https://comp110-26s.github.io/static/lessons/variables/` |
| Environment Diagrams topic | `env-classes.PNG`, `env-linked-list.PNG`, `env-recursion.PNG` under `https://comp110-26s.github.io/static/assets/env-diagrams/code-blocks/`; `classes-solution.png`, `recursion-solution.png`, `linked-list-solution.png` under `https://comp110-26s.github.io/static/assets/env-diagrams/diagrams/` |

## Slide PDFs With Memory-Diagram Mentions

The agenda links many PDFs. `pdftotext` scans found memory diagram or
stack/heap/function-call-frame content in these slide decks:

| Source | URL | Notes |
| --- | --- | --- |
| CL04 | https://comp110-26s.github.io/static/slides/cl04.pdf | Intro to memory diagrams. |
| CL04 annotated | https://comp110-26s.github.io/static/slides/cl04_annotated.pdf | Annotated intro, includes heap references. |
| CL05 | https://comp110-26s.github.io/static/slides/cl05.pdf | Memory diagram practice and CQ00 submission prompt. |
| CL06 | https://comp110-26s.github.io/static/slides/cl06.pdf | Contains a memory diagram slide. |
| CL07 | https://comp110-26s.github.io/static/slides/cl07.pdf | Contains a memory diagram slide. |
| CL12 | https://comp110-26s.github.io/static/slides/cl12.pdf | Recursion memory diagram / CQ01. |
| CL15 | https://comp110-26s.github.io/static/slides/cl15.pdf | Reference types; mentions memory diagram help. |
| CL16 blank | https://comp110-26s.github.io/static/slides/cl16_blank.pdf | Mentions memory diagram help. |
| CL18 | https://comp110-26s.github.io/static/slides/cl18.pdf | Contains a memory diagram slide. |
| CL20 | https://comp110-26s.github.io/static/slides/cl20.pdf | Contains a memory diagram slide. |
| CL24 | https://comp110-26s.github.io/static/slides/cl24.pdf | Contains a memory diagram slide. |
| CL25 | https://comp110-26s.github.io/static/slides/cl25.pdf | Contains multiple memory diagram slides. |
| CL29 | https://comp110-26s.github.io/static/slides/cl29.pdf | Contains a memory diagram slide. |
| CL31 | https://comp110-26s.github.io/static/slides/cl31.pdf | Contains a memory diagram slide. |
| CL33 | https://comp110-26s.github.io/static/slides/cl33.pdf | Mentions memory diagrams. |

## Coverage Implications For This App

1. The current source file `src/data/qz00Problems.ts` should not be treated as a
   complete 26S index while it still says it was generated from 24S materials.
2. Official-source regression tests should crawl or fixture the URLs above and
   fail when any indexed runnable code block is unsupported.
3. The importer needs a normalization layer for official HTML that can remove
   manual line numbers, repair common spacing artifacts, and preserve code
   indentation.
4. Parser coverage needs to grow beyond the QZ00-QZ02 happy path to support
   QZ03/environment-diagram syntax such as class examples, `from __future__
   import annotations`, `Node | None`, `is None`, and multi-line literals.
5. Visual comparison should not rely only on code blocks: official solution
   images are part of the source surface and should remain linked in the index.
