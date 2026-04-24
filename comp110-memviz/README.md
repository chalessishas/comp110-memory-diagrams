# COMP110 Memory Diagrams

Interactive Python memory-diagram visualizer for UNC COMP110, implementing the v0 ruleset used in the course.

**Live:** https://comp110-mem-diag.vercel.app/

Pick a practice problem, press Run, and step through the execution. Each snapshot renders the three-column diagram students draw by hand on quizzes:

- **Stack** — call frames with RA (return address), RV (return value), and bindings; retired frames stay visible as historical context
- **Heap** — typed objects with IDs (functions, classes, instances, lists, dicts)
- **Output** — what `print` wrote

When a value is reassigned the old value is struck through in place, matching the COMP110 grading convention.

## Features

- 39 curated practice problems across Basics, Conditionals, While loops, Functions, Lists, Dictionaries, Recursion, OOP, and OOP magic methods — sourced from the COMP110-24S practice page and verified to run
- Write-your-own Python sandbox (`Problem: Write your own`)
- Event-colored step timeline (declare / assign / call / return / print / control) — click any dot to jump
- Keyboard shortcuts for prev / next / auto-play / reset; per-button `<kbd>` chips show them inline
- Adjustable auto-play speed slider (200 – 2000 ms per step)
- Current-step line highlight in the editor, synced to the active snapshot
- `?embed=1` URL param strips header / footer / problem picker for iframe embedding; CSP allows `comp110-26s.github.io` and `*.unc.edu` as frame parents

## Supported Python

`def`, `class` (single inheritance), `return`, `if / elif / else`, `while`, `for`, `list`, `dict`, `+=`, `in`, `len()`, function calls, method calls, attribute access, and the `int / float / str / bool / None` base types. Runs in a tree-walking interpreter — not CPython — so only the v0 subset parses. `super()`, generators, decorators, comprehensions, exceptions, imports, and standard-library calls are intentionally out of scope.

## Local development

```bash
npm install
npm run dev        # Vite dev server at http://localhost:5173
npm run build      # type-check + bundle into dist/
npm test           # run vitest suites
npm run typecheck  # tsc --noEmit
```

## Architecture

Three files do most of the work:

- [`src/interpreter/evaluator.ts`](src/interpreter/evaluator.ts) — tree-walking interpreter; emits one `Snapshot` per observable state change
- [`src/components/DiagramCanvas.tsx`](src/components/DiagramCanvas.tsx) — renders a snapshot into the Stack / Heap / Output view
- [`src/App.tsx`](src/App.tsx) — state glue, problem picker, step controls, timeline, speed slider

The data model lives in [`src/interpreter/types.ts`](src/interpreter/types.ts). `Snapshot.event` classifies each step into one of seven categories (`declare | assign | call | return | print | control | meta`) which drives timeline dot colors.

## Credits

Built for [UNC COMP110](https://comp110-26s.github.io/). Implements the v0 memory-diagram rules from the course's [Rules PDF](https://comp110-26s.github.io/static/slides/memory_diagrams_v0.pdf), authored by the COMP110 teaching team.

## License

MIT — see [LICENSE](LICENSE).
