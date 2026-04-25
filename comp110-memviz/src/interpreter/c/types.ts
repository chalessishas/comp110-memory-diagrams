// Types for the C teaching-subset interpreter.
//
// Scope (intentionally small): int, char, int*/char* pointers, 1D int/char
// arrays, malloc/free, &/*, pointer arithmetic, printf("%d %c %s"),
// if/else, while, for, functions (no recursion limit hack), return.
// Out of scope: struct, typedef, function pointers, preprocessor (except
// stripping line comments), multi-file, file I/O.

import type { SnapshotEvent } from '../types'

// Static C types tracked per binding (C is statically typed, unlike our
// Python evaluator where every Binding carries any Value).
export type CType =
  | { kind: 'int' }
  | { kind: 'char' }
  | { kind: 'void' }
  | { kind: 'ptr'; to: CType }
  | { kind: 'arr'; of: CType; length: number }

// A concrete value flowing through the evaluator.
//   int / char  — primitive numeric value
//   ptr         — synthetic address into a CHeapBlock or a stack-resident
//                 array. address 0 = NULL.
//   uninit      — declared but never written. Reading it should be a UB
//                 warning the evaluator can choose to surface.
export type CValue =
  | { kind: 'int'; v: number }
  | { kind: 'char'; v: number } // 0..255
  | { kind: 'ptr'; address: number; pointsToType: CType }
  | { kind: 'uninit' }

// A binding inside a stack frame. Per the v0-mirror convention, reassignment
// retires the prior binding (strikethrough) instead of erasing it.
export type CBinding = {
  name: string
  type: CType
  value: CValue
  retired: boolean
}

// Stack frames mirror the Python model: Globals + one frame per active
// function call. retired=true once the function returned but we keep it
// visible (memviz convention).
export type CFrame = {
  name: string // "Globals" or function name like "main"
  returnAddress: number | null // line where call was made; null for Globals
  returnValue: CValue | null
  bindings: CBinding[]
  retired: boolean
}

// A heap block is what malloc returns. We model it as a contiguous array of
// CValue cells (so malloc(sizeof(int)*5) → 5 int cells). Each cell tracks
// retired state so writes show strikethrough history just like local vars.
export type CHeapCell = {
  index: number // 0..length-1
  value: CValue
  retired: boolean
}

export type CHeapBlock = {
  id: number // React key + identity
  address: number // synthetic, stable for the program lifetime
  size: number // total bytes (length * sizeof(elementType))
  elementType: CType
  length: number // number of cells
  cells: CHeapCell[]
  freed: boolean // set true after free(); we keep the block visible
}

// One observable step. Same shape as Python Snapshot but with C types so
// the C renderer doesn't have to discriminate.
export type CSnapshot = {
  step: number
  currentLine: number
  narration: string
  event: SnapshotEvent
  language: 'c'
  stack: CFrame[]
  heap: CHeapBlock[]
  output: string[]
  error: string | null
}

// AST ---------------------------------------------------------------

export type CProgram = {
  kind: 'program'
  body: CTopLevel[]
}

// Top-level forms only — globals + function definitions. No struct, no
// typedef, no #include parsing (we treat #include lines as comments).
export type CTopLevel = CFunctionDef | CVarDecl

export type CFunctionDef = {
  kind: 'funcDef'
  name: string
  returnType: CType
  params: { name: string; type: CType }[]
  body: CStmt[]
  lineStart: number
  lineEnd: number
}

export type CStmt =
  | CVarDecl
  | CAssignStmt
  | CIndexAssignStmt
  | CDerefAssignStmt
  | CIfStmt
  | CWhileStmt
  | CForStmt
  | CReturnStmt
  | CExprStmt
  | CBlockStmt

// `int x = 5;` or `int *p;` or `int arr[5];`
// At top level this is a global; inside a function this is a local decl.
export type CVarDecl = {
  kind: 'varDecl'
  type: CType
  name: string
  init: CExpr | null // null when uninitialized
  line: number
}

// `x = expr;` — bare name on LHS.
export type CAssignStmt = {
  kind: 'assign'
  target: string
  value: CExpr
  line: number
}

// `arr[i] = expr;` — index on LHS. target must be an array or pointer name.
export type CIndexAssignStmt = {
  kind: 'indexAssign'
  target: CExpr // usually a NameRef
  index: CExpr
  value: CExpr
  line: number
}

// `*p = expr;` — dereference assign. Pointer expression on LHS.
export type CDerefAssignStmt = {
  kind: 'derefAssign'
  target: CExpr // pointer expression
  value: CExpr
  line: number
}

export type CIfStmt = {
  kind: 'if'
  branches: { condition: CExpr; body: CStmt[] }[] // if + else-if chain
  elseBody: CStmt[] | null
  line: number
}

export type CWhileStmt = {
  kind: 'while'
  condition: CExpr
  body: CStmt[]
  line: number
}

export type CForStmt = {
  kind: 'for'
  // `for (init; cond; update) body` — init is a decl OR an expression OR null.
  init: CVarDecl | CExpr | null
  condition: CExpr | null // null = infinite
  update: CExpr | null
  body: CStmt[]
  line: number
}

export type CReturnStmt = {
  kind: 'return'
  expr: CExpr | null // null for `return;` from void
  line: number
}

export type CExprStmt = {
  kind: 'exprStmt'
  expr: CExpr
  line: number
}

export type CBlockStmt = {
  kind: 'block'
  body: CStmt[]
  line: number
}

export type CExpr =
  | CIntLit
  | CCharLit
  | CStrLit
  | CNameRef
  | CBinOp
  | CCmpOp
  | CLogicalOp
  | CNotOp
  | CUnaryOp
  | CAddrOf
  | CDeref
  | CCallExpr
  | CIndexExpr
  | CSizeofExpr
  | CCastExpr
  | CAssignExpr // C allows `x = 5` as expression (returns the value)

export type CIntLit = { kind: 'intLit'; v: number; line: number }
export type CCharLit = { kind: 'charLit'; v: number; line: number } // 'a' = 97
export type CStrLit = { kind: 'strLit'; v: string; line: number } // string literal → char* into a string-literal pool
export type CNameRef = { kind: 'name'; name: string; line: number }

export type CBinOp = {
  kind: 'binop'
  op: '+' | '-' | '*' | '/' | '%'
  left: CExpr
  right: CExpr
  line: number
}

export type CCmpOp = {
  kind: 'cmp'
  op: '==' | '!=' | '<' | '>' | '<=' | '>='
  left: CExpr
  right: CExpr
  line: number
}

export type CLogicalOp = {
  kind: 'logical'
  op: '&&' | '||'
  left: CExpr
  right: CExpr
  line: number
}

export type CNotOp = { kind: 'not'; operand: CExpr; line: number }
export type CUnaryOp = { kind: 'unop'; op: '-' | '+'; operand: CExpr; line: number }

// `&x` — produces a pointer to x.
export type CAddrOf = { kind: 'addrOf'; operand: CExpr; line: number }

// `*p` — read through a pointer.
export type CDeref = { kind: 'deref'; operand: CExpr; line: number }

// `f(a, b)` — function call. callee is a bare name (no function pointers).
export type CCallExpr = {
  kind: 'call'
  callee: string
  args: CExpr[]
  line: number
}

// `arr[i]` — read from array/pointer.
export type CIndexExpr = {
  kind: 'index'
  target: CExpr
  index: CExpr
  line: number
}

// `sizeof(int)` or `sizeof(int*)` — only type-sizeof, no expression-sizeof.
export type CSizeofExpr = { kind: 'sizeof'; type: CType; line: number }

// `(int*) malloc(n)` — only used in front of malloc; we accept any cast but
// just propagate the inner expression at runtime.
export type CCastExpr = { kind: 'cast'; type: CType; expr: CExpr; line: number }

// `x = expr` as expression (allowed inside `for` updates). Returns expr value.
export type CAssignExpr = {
  kind: 'assignExpr'
  target: string
  value: CExpr
  line: number
}
