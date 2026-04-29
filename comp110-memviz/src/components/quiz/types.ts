// Quiz Practice — knowledge-organized question bank schema.
// Topics are concept-based, not quiz-numbered, so the same kind of
// question (e.g., "identify lines that are function signatures") can
// pull from QZ00 Q3 and QZ03 Q3 in one drill.

export type Topic =
  | 'types-expressions'
  | 'functions-anatomy'
  | 'function-writing'
  | 'conditionals-boolean'
  | 'recursion'
  | 'looping'
  | 'collections'
  | 'function-writing-full'
  | 'classes'
  | 'class-writing'
  | 'linked-lists'
  | 'memory-diagrams'

export const TOPIC_META: Record<Topic, { label: string; description: string }> = {
  'types-expressions': {
    label: 'Types & Expressions',
    description: 'int / float / str / bool casts, arithmetic, % // **, string concatenation',
  },
  'functions-anatomy': {
    label: 'Function Anatomy',
    description: 'Identify signatures, parameters, arguments, docstrings, return statements, unreachable code',
  },
  'function-writing': {
    label: 'Function Signatures & Calls',
    description: 'Write explicitly-typed signatures and matching calls',
  },
  'conditionals-boolean': {
    label: 'Conditionals & Boolean Logic',
    description: 'and / or / not, operator precedence, flattening nested if',
  },
  recursion: {
    label: 'Recursion',
    description: 'Base case, recursive case, edge case, infinite recursion',
  },
  looping: {
    label: 'Looping',
    description: 'for / while, range, iterating dicts/sets/lists',
  },
  collections: {
    label: 'Collections (list / set / dict)',
    description: 'Properties, literal syntax, mutation methods',
  },
  'function-writing-full': {
    label: 'Function Writing (full body)',
    description: 'Write a complete function definition with explicit types',
  },
  classes: {
    label: 'Classes & OOP',
    description: 'Instantiation, self, __init__, attribute access, method calls',
  },
  'class-writing': {
    label: 'Class Definition Writing',
    description: 'Write a class from a description, with constructor and methods',
  },
  'linked-lists': {
    label: 'Linked Lists',
    description: 'Recursive data structures, traversal, __str__ / __repr__',
  },
  'memory-diagrams': {
    label: 'Memory Diagrams',
    description: 'Trace globals, stack frames, heap, output — uses the live interpreter',
  },
}

// One choice per bubble. Display in vertical list, fixed-width letters
// (a, b, c, ...) on the left to mimic the printed quiz.
export type Choice = { label: string; value: string }

// Partial-credit rule — the rubric scores deductions for things like
// missing quotes around a string answer. We surface them as soft hints
// rather than docking points, since this is for self-study.
export type PartialCreditRule = { description: string; deduction: number }

export type BaseQuestion = {
  id: string
  topic: Topic
  // Where the question came from in the original PDFs, e.g. "QZ00 Q1.1".
  source?: string
  prompt: string
  // Optional Python code shown above the answer area (numbered, monospace).
  code?: string
}

export type MCQQuestion = BaseQuestion & {
  type: 'mcq'
  choices: Choice[]
  // Index into `choices`.
  answer: number
  explanation?: string
}

export type EvaluateQuestion = BaseQuestion & {
  type: 'evaluate'
  // Accepted forms for the value. Comparison is exact-string after trim.
  // For "Amount: 6" we accept both `"Amount: 6"` and `Amount: 6` and
  // mark the latter as a partial credit (no quotes).
  acceptedValues: string[]
  preferredValue: string
  // Mirrors the rubric's "Correct Type" sub-point.
  acceptedTypes: string[]
  preferredType: string
  partialCreditRules?: PartialCreditRule[]
  // For "Error" expressions there's no type.
  isError?: boolean
  explanation?: string
}

export type IdentifyLinesQuestion = BaseQuestion & {
  type: 'identify-lines'
  // The line numbers a student can choose between.
  lineOptions: number[]
  // Correct line numbers. Order doesn't matter.
  answer: number[]
  // If 'per-line', partial credit equal to (correct picks / total correct).
  scoring: 'all-or-nothing' | 'per-line'
  // For questions whose accepted answer set has a "(or X and Y)" variant.
  alternateAnswers?: number[][]
  explanation?: string
}

export type WriteCodeValidator =
  | { kind: 'regex'; pattern: string; flags?: string; weight: number; label: string }
  | { kind: 'contains'; needle: string; weight: number; label: string }
  | { kind: 'not-contains'; needle: string; weight: number; label: string }

export type WriteCodeQuestion = BaseQuestion & {
  type: 'write-code'
  // Multi-line allowed. Shown in a CodeMirror editor seeded with `template`.
  template?: string
  validators: WriteCodeValidator[]
  // Reference solution shown after Submit.
  sampleAnswer: string
  partialCreditRules?: PartialCreditRule[]
}

export type MemoryDiagramQuestion = BaseQuestion & {
  type: 'memory-diagram'
  // Python source the student needs to trace. Named `program` (not
  // `source`) to avoid shadowing BaseQuestion.source, which holds the
  // citation like "QZ00 Q5". Piped into the existing interpreter.
  program: string
  // What gets printed (rendered after Submit so students can self-check
  // their hand-traced output).
  expectedOutput: string
}

export type Question =
  | MCQQuestion
  | EvaluateQuestion
  | IdentifyLinesQuestion
  | WriteCodeQuestion
  | MemoryDiagramQuestion
