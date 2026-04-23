// Types for the COMP110 v0 Python memory diagram model.
// These mirror the rules in memory_diagrams_v0.pdf.

export type Value =
  | { kind: 'int'; v: number }
  | { kind: 'float'; v: number }
  | { kind: 'str'; v: string }
  | { kind: 'none' }
  | { kind: 'ref'; id: number } // reference to a heap object

export type HeapObject = {
  id: number
  kind: 'function'
  name: string
  lineStart: number
  lineEnd: number
}

// Per the v0 ruleset, variable assignments and function returns don't erase
// the old value — the prior value/frame is struck-through and stays visible.
// We model that with `retired: boolean` on both bindings and frames.
export type Binding = {
  name: string
  value: Value
  retired: boolean
}

export type Frame = {
  name: string // "Globals" or function name
  returnAddress: number | null // line number where the call was made (null for Globals)
  returnValue: Value | null
  bindings: Binding[]
  retired: boolean // true once the function has returned; frame stays visible
}

// A single step the student can observe. The evaluator produces a list of
// Snapshots that the UI renders as the user clicks next/prev.
export type Snapshot = {
  step: number
  // 1-based line number the student should look at. 0 if program start / end.
  currentLine: number
  // Short English description of what just happened. Shown under the diagram.
  narration: string
  // Frame at index 0 is Globals; last element is the active frame.
  stack: Frame[]
  heap: HeapObject[]
  output: string[]
  error: string | null
}

// AST ---------------------------------------------------------------

export type TypeAnnotation = 'int' | 'float' | 'str' | 'None' | 'bool' | string

export type Param = {
  name: string
  type: TypeAnnotation
}

export type Program = {
  kind: 'program'
  body: Stmt[]
}

export type Stmt =
  | FunctionDef
  | ReturnStmt
  | ExprStmt

export type FunctionDef = {
  kind: 'funcDef'
  name: string
  params: Param[]
  returnType: TypeAnnotation
  body: Stmt[]
  lineStart: number
  lineEnd: number
}

export type ReturnStmt = {
  kind: 'return'
  expr: Expr | null
  line: number
}

export type ExprStmt = {
  kind: 'exprStmt'
  expr: Expr
  line: number
}

export type Expr =
  | NumLit
  | StrLit
  | NameRef
  | BinaryOp
  | UnaryOp
  | CallExpr
  | IndexExpr

export type NumLit = { kind: 'num'; v: number; isFloat: boolean; line: number }
export type StrLit = { kind: 'str'; v: string; line: number }
export type NameRef = { kind: 'name'; name: string; line: number }
export type BinaryOp = {
  kind: 'binop'
  op: '+' | '-' | '*' | '/' | '//' | '%' | '**'
  left: Expr
  right: Expr
  line: number
}
export type UnaryOp = { kind: 'unop'; op: '-' | '+'; operand: Expr; line: number }
export type CallExpr = {
  kind: 'call'
  callee: string // simple names only in v0
  args: { name: string | null; value: Expr }[] // name=null → positional
  line: number
}
export type IndexExpr = {
  kind: 'index'
  target: Expr
  index: Expr
  line: number
}
