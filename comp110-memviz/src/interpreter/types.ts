// Types for the COMP110 v0 Python memory diagram model.
// These mirror the rules in memory_diagrams_v0.pdf.

export type Value =
  | { kind: 'int'; v: number }
  | { kind: 'float'; v: number }
  | { kind: 'str'; v: string }
  | { kind: 'bool'; v: boolean }
  | { kind: 'none' }
  | { kind: 'ref'; id: number } // reference to a heap object

export type HeapObject = HeapFunction | HeapClass | HeapInstance

export type HeapFunction = {
  id: number
  kind: 'function'
  name: string
  lineStart: number
  lineEnd: number
}

export type HeapClass = {
  id: number
  kind: 'class'
  name: string
  lineStart: number
  lineEnd: number
  methodNames: string[] // for display in the heap column
}

// An instance stores its attributes as a Binding[] so attribute
// reassignment produces the same strike-through rendering students see
// for local-variable rebinding.
export type HeapInstance = {
  id: number
  kind: 'instance'
  className: string
  classId: number
  attrs: Binding[]
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
  | AssignStmt
  | AttrAssignStmt
  | IfStmt
  | ClassDef

export type AssignStmt = {
  kind: 'assign'
  target: string // simple names only in v0
  typeAnnotation: TypeAnnotation | null // present on first declaration: `a: int = 3`
  value: Expr
  line: number
}

export type AttrAssignStmt = {
  kind: 'attrAssign'
  target: Expr // the object whose attribute is being written (usually `self` or a name)
  attr: string
  value: Expr
  line: number
}

export type IfStmt = {
  kind: 'if'
  branches: { condition: Expr; body: Stmt[] }[] // if + any elifs
  elseBody: Stmt[] | null
  line: number
}

export type ClassDef = {
  kind: 'classDef'
  name: string
  // Bare field declarations inside the class body: `name: str`. v0.1 treats
  // these as documentation only — the actual value lives on the instance.
  fieldDecls: { name: string; type: TypeAnnotation }[]
  methods: FunctionDef[]
  lineStart: number
  lineEnd: number
}

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
  | FStringLit
  | BoolLit
  | NameRef
  | BinaryOp
  | CompareOp
  | BoolOp
  | NotOp
  | UnaryOp
  | CallExpr
  | IndexExpr
  | AttrExpr

export type NumLit = { kind: 'num'; v: number; isFloat: boolean; line: number }
export type StrLit = { kind: 'str'; v: string; line: number }
export type FStringLit = {
  kind: 'fstr'
  // A sequence of alternating literal chunks and interpolated expressions.
  parts: ({ kind: 'lit'; v: string } | { kind: 'interp'; expr: Expr })[]
  line: number
}
export type BoolLit = { kind: 'bool'; v: boolean; line: number }
export type NameRef = { kind: 'name'; name: string; line: number }
export type CompareOp = {
  kind: 'cmp'
  op: '==' | '!=' | '<' | '>' | '<=' | '>='
  left: Expr
  right: Expr
  line: number
}
export type BoolOp = {
  kind: 'boolOp'
  op: 'and' | 'or'
  left: Expr
  right: Expr
  line: number
}
export type NotOp = { kind: 'not'; operand: Expr; line: number }
export type AttrExpr = { kind: 'attr'; target: Expr; name: string; line: number }
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
  callee: string // simple name (for bare `foo(...)`) or method name (for `obj.foo(...)`)
  // When present, this is a method call — look up `callee` on the object this
  // expression evaluates to, and pass the object as the first arg (self).
  methodOf?: Expr
  args: { name: string | null; value: Expr }[] // name=null → positional
  line: number
}
export type IndexExpr = {
  kind: 'index'
  target: Expr
  index: Expr
  line: number
}
