// Evaluator for the COMP110 v0 Python subset.
// Walks the AST, produces a list of Snapshots the UI steps through.
//
// Semantics are tuned to match memory_diagrams_v0.pdf exactly:
// - Function definitions create a heap object ID:N and bind the name in
//   the current frame.
// - A function call creates a new stack frame with RA (return address) set
//   to the call site's line, then jumps to the first body statement.
// - Return evaluates the expression, stores RV in the current frame, then
//   the frame is popped.
// - Built-ins (print, len, int, str, float) do NOT create a stack frame
//   (per the PDF — they're inline evaluations).
// - Name resolution: current frame → globals → NameError.

import type {
  Binding,
  CallExpr,
  Expr,
  FunctionDef,
  Frame,
  HeapObject,
  Program,
  Snapshot,
  Stmt,
  Value,
} from './types'
import { parse } from './parser'

class ReturnSignal {
  value: Value
  constructor(value: Value) {
    this.value = value
  }
}

class RuntimeErrorSignal extends Error {
  line: number
  constructor(message: string, line: number) {
    super(message)
    this.line = line
  }
}

type State = {
  stack: Frame[]
  heap: HeapObject[]
  output: string[]
  nextHeapId: number
  funcDefs: Map<string, FunctionDef>
  snapshots: Snapshot[]
}

function cloneValue(v: Value): Value {
  return { ...v }
}

function cloneFrame(f: Frame): Frame {
  return {
    name: f.name,
    returnAddress: f.returnAddress,
    returnValue: f.returnValue ? cloneValue(f.returnValue) : null,
    bindings: f.bindings.map((b) => ({
      name: b.name,
      value: cloneValue(b.value),
      retired: b.retired,
    })),
    retired: f.retired,
  }
}

// Retire the prior active binding of `name` (if any) and push a new active one.
// Mirrors the PDF rule: rebinding strikes through the old value and writes a
// new line beneath it.
function setBinding(frame: Frame, name: string, value: Value) {
  for (const b of frame.bindings) {
    if (!b.retired && b.name === name) b.retired = true
  }
  frame.bindings.push({ name, value, retired: false })
}

// Return the most-recent non-retired binding for `name`, or undefined.
function lookupBinding(frame: Frame, name: string): Value | undefined {
  for (let i = frame.bindings.length - 1; i >= 0; i--) {
    const b = frame.bindings[i]
    if (!b.retired && b.name === name) return b.value
  }
  return undefined
}

function snap(state: State, currentLine: number, narration: string, error: string | null = null): Snapshot {
  return {
    step: state.snapshots.length,
    currentLine,
    narration,
    stack: state.stack.map(cloneFrame),
    heap: state.heap.map((h) => ({ ...h })),
    output: [...state.output],
    error,
  }
}

function push(state: State, snapshot: Snapshot) {
  state.snapshots.push(snapshot)
}

const BUILTINS = new Set(['print', 'len', 'int', 'str', 'float'])

// The active frame is the topmost non-retired frame. Retired frames stay in
// the stack for visualization but aren't the "current" execution context.
function currentFrame(state: State): Frame {
  for (let i = state.stack.length - 1; i >= 0; i--) {
    if (!state.stack[i].retired) return state.stack[i]
  }
  throw new Error('invariant: no active frame')
}

function globalsFrame(state: State): Frame {
  return state.stack[0]
}

function resolveName(state: State, name: string, line: number): Value {
  // Literal keywords that read as names.
  if (name === 'None') return { kind: 'none' }
  if (name === 'True') return { kind: 'int', v: 1 }
  if (name === 'False') return { kind: 'int', v: 0 }

  const cur = currentFrame(state)
  const local = lookupBinding(cur, name)
  if (local !== undefined) return local
  if (cur !== globalsFrame(state)) {
    const g = lookupBinding(globalsFrame(state), name)
    if (g !== undefined) return g
  }
  if (BUILTINS.has(name)) {
    // Represent built-ins as a special marker so the call logic can detect them.
    return { kind: 'str', v: `__builtin_${name}` } as Value
  }
  throw new RuntimeErrorSignal(`NameError on line ${line}: name '${name}' is not defined`, line)
}

function valueToDisplay(v: Value, state: State): string {
  if (v.kind === 'int') return String(v.v)
  if (v.kind === 'float') return Number.isInteger(v.v) ? `${v.v}.0` : String(v.v)
  if (v.kind === 'str') return v.v
  if (v.kind === 'none') return 'None'
  if (v.kind === 'ref') {
    const obj = state.heap.find((h) => h.id === v.id)
    return obj ? `ID:${v.id} (${obj.name})` : `ID:${v.id}`
  }
  return '?'
}

function evalExpr(state: State, expr: Expr): Value {
  switch (expr.kind) {
    case 'num':
      return expr.isFloat ? { kind: 'float', v: expr.v } : { kind: 'int', v: expr.v }
    case 'str':
      return { kind: 'str', v: expr.v }
    case 'name':
      return resolveName(state, expr.name, expr.line)
    case 'unop': {
      const v = evalExpr(state, expr.operand)
      if (v.kind !== 'int' && v.kind !== 'float') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${expr.line}: unary ${expr.op} on ${v.kind}`,
          expr.line,
        )
      }
      const r = expr.op === '-' ? -v.v : v.v
      return v.kind === 'int' ? { kind: 'int', v: r } : { kind: 'float', v: r }
    }
    case 'binop':
      return evalBinop(state, expr)
    case 'call':
      return evalCall(state, expr)
    case 'index': {
      const target = evalExpr(state, expr.target)
      const idx = evalExpr(state, expr.index)
      if (target.kind !== 'str') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${expr.line}: only strings support indexing in v0`,
          expr.line,
        )
      }
      if (idx.kind !== 'int') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${expr.line}: string index must be int`,
          expr.line,
        )
      }
      const i = idx.v < 0 ? target.v.length + idx.v : idx.v
      if (i < 0 || i >= target.v.length) {
        throw new RuntimeErrorSignal(
          `IndexError on line ${expr.line}: string index ${idx.v} out of range`,
          expr.line,
        )
      }
      return { kind: 'str', v: target.v[i] }
    }
  }
}

function evalBinop(state: State, expr: Expr & { kind: 'binop' }): Value {
  const l = evalExpr(state, expr.left)
  const r = evalExpr(state, expr.right)

  // String concatenation.
  if (expr.op === '+' && l.kind === 'str' && r.kind === 'str') {
    return { kind: 'str', v: l.v + r.v }
  }
  if (l.kind !== 'int' && l.kind !== 'float') {
    throw new RuntimeErrorSignal(`TypeError on line ${expr.line}: left of '${expr.op}' is ${l.kind}`, expr.line)
  }
  if (r.kind !== 'int' && r.kind !== 'float') {
    throw new RuntimeErrorSignal(`TypeError on line ${expr.line}: right of '${expr.op}' is ${r.kind}`, expr.line)
  }
  const lv = l.v, rv = r.v
  let result: number
  switch (expr.op) {
    case '+': result = lv + rv; break
    case '-': result = lv - rv; break
    case '*': result = lv * rv; break
    case '/': {
      if (rv === 0) throw new RuntimeErrorSignal(`ZeroDivisionError on line ${expr.line}`, expr.line)
      // '/' always yields float in Python 3.
      return { kind: 'float', v: lv / rv }
    }
    case '//': {
      if (rv === 0) throw new RuntimeErrorSignal(`ZeroDivisionError on line ${expr.line}`, expr.line)
      result = Math.floor(lv / rv)
      break
    }
    case '%': {
      if (rv === 0) throw new RuntimeErrorSignal(`ZeroDivisionError on line ${expr.line}`, expr.line)
      result = lv - Math.floor(lv / rv) * rv
      break
    }
    case '**': result = Math.pow(lv, rv); break
  }
  // If either operand is float, result is float.
  if (l.kind === 'float' || r.kind === 'float') return { kind: 'float', v: result }
  return { kind: 'int', v: result }
}

function evalCall(state: State, expr: CallExpr): Value {
  // Evaluate args left-to-right.
  const argValues = expr.args.map((a) => ({ name: a.name, value: evalExpr(state, a.value) }))

  // Built-ins: no stack frame created.
  if (BUILTINS.has(expr.callee)) {
    return applyBuiltin(state, expr, argValues)
  }

  // User function — look up heap object via name resolution in current frame.
  const ref = resolveName(state, expr.callee, expr.line)
  if (ref.kind !== 'ref') {
    throw new RuntimeErrorSignal(
      `TypeError on line ${expr.line}: '${expr.callee}' is not callable`,
      expr.line,
    )
  }
  const fn = state.funcDefs.get(expr.callee)
  if (!fn) {
    throw new RuntimeErrorSignal(
      `NameError on line ${expr.line}: function '${expr.callee}' not defined`,
      expr.line,
    )
  }

  // Bind arguments to parameters. v0 accepts both positional and kwarg.
  if (argValues.length !== fn.params.length) {
    throw new RuntimeErrorSignal(
      `Function Call Error on Line ${expr.line}: ${expr.callee} expects ${fn.params.length} arg(s), got ${argValues.length}`,
      expr.line,
    )
  }
  const paramValues: Record<string, Value> = {}
  const used = new Set<string>()
  for (let i = 0; i < argValues.length; i++) {
    const { name, value } = argValues[i]
    if (name !== null) {
      const p = fn.params.find((p) => p.name === name)
      if (!p) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${expr.line}: unknown keyword '${name}' for ${expr.callee}`,
          expr.line,
        )
      }
      if (used.has(name)) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${expr.line}: duplicate keyword '${name}'`,
          expr.line,
        )
      }
      used.add(name)
      paramValues[name] = value
    } else {
      const p = fn.params[i]
      if (!p || used.has(p.name)) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${expr.line}: too many positional args for ${expr.callee}`,
          expr.line,
        )
      }
      used.add(p.name)
      paramValues[p.name] = value
    }
  }
  for (const p of fn.params) {
    if (!(p.name in paramValues)) {
      throw new RuntimeErrorSignal(
        `Function Call Error on Line ${expr.line}: missing argument '${p.name}' for ${expr.callee}`,
        expr.line,
      )
    }
  }

  // Build bindings in declaration order so the diagram shows params top-to-bottom
  // matching the def.
  const bindings: Binding[] = fn.params.map((p) => ({
    name: p.name,
    value: paramValues[p.name],
    retired: false,
  }))

  // Push the new frame and snapshot the entry.
  const newFrame: Frame = {
    name: expr.callee,
    returnAddress: expr.line,
    returnValue: null,
    bindings,
    retired: false,
  }
  state.stack.push(newFrame)
  const argsList = fn.params.map((p) => `${p.name}=${valueToDisplay(paramValues[p.name], state)}`).join(', ')
  push(state, snap(state, fn.lineStart, `Call ${expr.callee}(${argsList}). New frame pushed; jumping to line ${fn.lineStart}.`))

  // Execute the body.
  let rv: Value = { kind: 'none' }
  try {
    for (const stmt of fn.body) execStmt(state, stmt)
  } catch (e) {
    if (e instanceof ReturnSignal) rv = e.value
    else throw e
  }

  // Record the RV on the frame, mark the frame retired (strike-through), then
  // snapshot. The frame stays in the stack for visualization — the next
  // activeFrame lookup will skip it.
  newFrame.returnValue = rv
  newFrame.retired = true
  push(
    state,
    snap(
      state,
      newFrame.returnAddress ?? fn.lineEnd,
      `Return from ${expr.callee} with RV = ${valueToDisplay(rv, state)}. Frame retired (struck through). Jumping back to line ${newFrame.returnAddress}.`,
    ),
  )
  return rv
}

function applyBuiltin(
  state: State,
  expr: CallExpr,
  args: { name: string | null; value: Value }[],
): Value {
  const name = expr.callee
  const values = args.map((a) => a.value)
  switch (name) {
    case 'print': {
      if (values.length !== 1) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${expr.line}: print takes 1 arg, got ${values.length}`,
          expr.line,
        )
      }
      const line = valueToDisplay(values[0], state)
      state.output.push(line)
      push(state, snap(state, expr.line, `Printed '${line}' to Output.`))
      return { kind: 'none' }
    }
    case 'len': {
      if (values.length !== 1 || values[0].kind !== 'str') {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${expr.line}: len() expects one string argument`,
          expr.line,
        )
      }
      return { kind: 'int', v: values[0].v.length }
    }
    case 'int': {
      if (values.length !== 1) throw new RuntimeErrorSignal(`int() takes 1 arg`, expr.line)
      const v = values[0]
      if (v.kind === 'int') return v
      if (v.kind === 'float') return { kind: 'int', v: Math.trunc(v.v) }
      if (v.kind === 'str') {
        const n = Number(v.v)
        if (Number.isNaN(n)) throw new RuntimeErrorSignal(`ValueError: invalid int: '${v.v}'`, expr.line)
        return { kind: 'int', v: Math.trunc(n) }
      }
      throw new RuntimeErrorSignal(`int() on unsupported type`, expr.line)
    }
    case 'float': {
      if (values.length !== 1) throw new RuntimeErrorSignal(`float() takes 1 arg`, expr.line)
      const v = values[0]
      if (v.kind === 'int' || v.kind === 'float') return { kind: 'float', v: v.v }
      if (v.kind === 'str') {
        const n = Number(v.v)
        if (Number.isNaN(n)) throw new RuntimeErrorSignal(`ValueError: invalid float: '${v.v}'`, expr.line)
        return { kind: 'float', v: n }
      }
      throw new RuntimeErrorSignal(`float() on unsupported type`, expr.line)
    }
    case 'str': {
      if (values.length !== 1) throw new RuntimeErrorSignal(`str() takes 1 arg`, expr.line)
      return { kind: 'str', v: valueToDisplay(values[0], state) }
    }
  }
  throw new RuntimeErrorSignal(`unknown built-in '${name}'`, expr.line)
}

function execStmt(state: State, stmt: Stmt) {
  switch (stmt.kind) {
    case 'funcDef':
      addFuncDef(state, stmt)
      return
    case 'return': {
      const v = stmt.expr ? evalExpr(state, stmt.expr) : ({ kind: 'none' } as Value)
      throw new ReturnSignal(v)
    }
    case 'exprStmt': {
      evalExpr(state, stmt.expr)
      return
    }
  }
}

function addFuncDef(state: State, fn: FunctionDef) {
  state.funcDefs.set(fn.name, fn)
  const id = state.nextHeapId++
  state.heap.push({
    id,
    kind: 'function',
    name: fn.name,
    lineStart: fn.lineStart,
    lineEnd: fn.lineEnd,
  })
  const frame = currentFrame(state)
  setBinding(frame, fn.name, { kind: 'ref', id })
  push(
    state,
    snap(
      state,
      fn.lineStart,
      `Defined function '${fn.name}' (lines ${fn.lineStart}-${fn.lineEnd}). Heap ID:${id} created; '${fn.name}' bound in current frame.`,
    ),
  )
}

export function evaluate(program: Program): Snapshot[] {
  const state: State = {
    stack: [
      {
        name: 'Globals',
        returnAddress: null,
        returnValue: null,
        bindings: [],
        retired: false,
      },
    ],
    heap: [],
    output: [],
    nextHeapId: 0,
    funcDefs: new Map(),
    snapshots: [],
  }

  push(state, snap(state, 1, 'Program start. Globals frame created; beginning line-by-line evaluation.'))

  try {
    for (const stmt of program.body) {
      execStmt(state, stmt)
    }
    push(state, snap(state, 0, 'Program complete.'))
  } catch (e) {
    if (e instanceof RuntimeErrorSignal) {
      push(state, snap(state, e.line, 'Execution halted due to error.', e.message))
    } else if (e instanceof ReturnSignal) {
      // Stray return at module level is a syntax-esque error in v0.
      push(state, snap(state, 0, 'Return at module scope.', 'SyntaxError: return outside function'))
    } else {
      throw e
    }
  }
  return state.snapshots
}

export function run(src: string): Snapshot[] {
  return evaluate(parse(src))
}
