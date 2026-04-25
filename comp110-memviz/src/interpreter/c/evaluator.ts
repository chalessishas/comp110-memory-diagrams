// C tree-walking evaluator (MVP scope).
//
// Implemented:  int / char vars, arithmetic, comparison, logical, printf
//               (%d %c %s with string literals only), if/else, while, for,
//               function definitions + call/return.
// Deferred:     pointers (& *), malloc/free, arrays, char* string indexing.
//
// The evaluator emits a Snapshot before each statement executes (so the
// timeline shows "about to run line N") and after key effects (assignment,
// print, frame push/pop). Same vocabulary as the Python evaluator's snap()
// helper so the UI can stay uniform.

import type {
  CBinding, CExpr, CFrame, CFunctionDef, CHeapBlock, CSnapshot,
  CStmt, CType, CValue, CVarDecl,
} from './types'
import type { SnapshotEvent } from '../types'
import { tokenizeC } from './tokenizer'
import { parseC } from './parser'

// Per-step state. The evaluator mutates this in place and clones into a
// Snapshot via snap(). Snapshots are deep-cloned so timeline navigation
// shows historical state, not live state.
type State = {
  stack: CFrame[]
  heap: CHeapBlock[]
  output: string[]
  snapshots: CSnapshot[]
  functions: Map<string, CFunctionDef>
  // Step counter feeds Snapshot.step.
  step: number
}

export class CRuntimeError extends Error {
  line: number
  constructor(message: string, line: number) {
    super(`Runtime error on line ${line}: ${message}`)
    this.line = line
  }
}

// Top-level entry — tokenize → parse → evaluate.
export function runC(src: string): CSnapshot[] {
  const tokens = tokenizeC(src)
  const program = parseC(tokens)

  const state: State = {
    stack: [{ name: 'Globals', returnAddress: null, returnValue: null, bindings: [], retired: false }],
    heap: [],
    output: [],
    snapshots: [],
    functions: new Map(),
    step: 0,
  }

  // First pass: collect function definitions (so calls can refer to them
  // regardless of source order).
  for (const top of program.body) {
    if (top.kind === 'funcDef') {
      state.functions.set(top.name, top)
    }
  }

  // Snap a "program start" frame so the timeline has an initial state.
  snap(state, 0, `Program starts. Globals frame opens.`, 'meta')

  // Execute global declarations first (function defs are no-ops at runtime).
  for (const top of program.body) {
    if (top.kind === 'varDecl') execVarDecl(state, top)
  }

  // Find main() and call it. C programs without main() are an error.
  const main = state.functions.get('main')
  if (!main) {
    snap(state, 0, `Error: program has no main() function.`, 'meta', `program has no main() function`)
    return state.snapshots
  }

  let errored = false
  try {
    callFunction(state, main, [], 0)
  } catch (e) {
    if (e instanceof CRuntimeError) {
      snap(state, e.line, e.message, 'meta', e.message)
      errored = true
    } else if (e instanceof ReturnSignal) {
      // main returned — that's fine.
    } else {
      throw e
    }
  }

  if (!errored) snap(state, 0, `Program ends.`, 'meta')
  return state.snapshots
}

// ---------------------------------------------------------------- snap

function snap(
  state: State,
  currentLine: number,
  narration: string,
  event: SnapshotEvent,
  error: string | null = null,
): void {
  state.snapshots.push({
    step: state.step++,
    currentLine,
    narration,
    event,
    language: 'c',
    stack: cloneStack(state.stack),
    heap: cloneHeap(state.heap),
    output: [...state.output],
    error,
  })
}

function cloneStack(stack: CFrame[]): CFrame[] {
  return stack.map((f) => ({
    ...f,
    bindings: f.bindings.map((b) => ({ ...b, value: cloneValue(b.value), type: cloneType(b.type) })),
    returnValue: f.returnValue ? cloneValue(f.returnValue) : null,
  }))
}

function cloneHeap(heap: CHeapBlock[]): CHeapBlock[] {
  return heap.map((h) => ({
    ...h,
    elementType: cloneType(h.elementType),
    cells: h.cells.map((c) => ({ ...c, value: cloneValue(c.value) })),
  }))
}

function cloneValue(v: CValue): CValue {
  // Values are immutable union members; shallow copy is safe.
  return { ...v } as CValue
}

function cloneType(t: CType): CType {
  if (t.kind === 'ptr') return { kind: 'ptr', to: cloneType(t.to) }
  if (t.kind === 'arr') return { kind: 'arr', of: cloneType(t.of), length: t.length }
  return { ...t }
}

// ---------------------------------------------------------------- statements

function execStmt(state: State, stmt: CStmt): void {
  switch (stmt.kind) {
    case 'varDecl': return execVarDecl(state, stmt)
    case 'assign': return execAssign(state, stmt)
    case 'exprStmt': return execExprStmt(state, stmt)
    case 'if': return execIf(state, stmt)
    case 'while': return execWhile(state, stmt)
    case 'for': return execFor(state, stmt)
    case 'return': return execReturn(state, stmt)
    case 'block':
      for (const s of stmt.body) execStmt(state, s)
      return
    case 'indexAssign':
    case 'derefAssign':
      throw new CRuntimeError(`pointer/array writes are not supported in this MVP yet`, stmt.line)
  }
}

function execVarDecl(state: State, stmt: CVarDecl): void {
  const frame = topFrame(state)
  const initValue: CValue = stmt.init !== null ? evalExpr(state, stmt.init) : { kind: 'uninit' }
  const coerced = coerceToType(initValue, stmt.type, stmt.line)
  // Retire any prior binding with the same name in this frame.
  for (const b of frame.bindings) {
    if (b.name === stmt.name && !b.retired) b.retired = true
  }
  frame.bindings.push({ name: stmt.name, type: stmt.type, value: coerced, retired: false })
  const desc = stmt.init !== null
    ? `Declare ${typeToStr(stmt.type)} ${stmt.name} = ${valueToDisplay(coerced)}.`
    : `Declare ${typeToStr(stmt.type)} ${stmt.name} (uninitialized).`
  snap(state, stmt.line, desc, 'declare')
}

function execAssign(state: State, stmt: { target: string; value: CExpr; line: number }): void {
  const frame = topFrame(state)
  const target = lookupBinding(state, stmt.target)
  if (target === null) {
    throw new CRuntimeError(`unknown variable '${stmt.target}'`, stmt.line)
  }
  const newValue = coerceToType(evalExpr(state, stmt.value), target.binding.type, stmt.line)
  // Retire the prior binding in the frame where it lives, push new entry.
  target.binding.retired = true
  target.frame.bindings.push({
    name: stmt.target,
    type: cloneType(target.binding.type),
    value: newValue,
    retired: false,
  })
  // Use frame for narration but assignment doesn't depend on which frame —
  // just keep the current one for line tracking.
  void frame
  snap(state, stmt.line, `${stmt.target} = ${valueToDisplay(newValue)}.`, 'assign')
}

function execExprStmt(state: State, stmt: { expr: CExpr; line: number }): void {
  // Evaluate for side effects only (function calls, mostly).
  evalExpr(state, stmt.expr)
}

function execIf(state: State, stmt: { branches: { condition: CExpr; body: CStmt[] }[]; elseBody: CStmt[] | null; line: number }): void {
  for (let i = 0; i < stmt.branches.length; i++) {
    const branch = stmt.branches[i]
    const c = evalExpr(state, branch.condition)
    if (truthy(c)) {
      const tag = i === 0 ? 'if' : 'else if'
      snap(state, branch.condition.line, `Condition true — entering ${tag} branch.`, 'control')
      for (const s of branch.body) execStmt(state, s)
      return
    }
  }
  if (stmt.elseBody) {
    snap(state, stmt.line, `All conditions false — entering else branch.`, 'control')
    for (const s of stmt.elseBody) execStmt(state, s)
  } else {
    snap(state, stmt.line, `All conditions false — skipping if.`, 'control')
  }
}

function execWhile(state: State, stmt: { condition: CExpr; body: CStmt[]; line: number }): void {
  let iter = 0
  while (true) {
    iter++
    const c = evalExpr(state, stmt.condition)
    if (!truthy(c)) {
      snap(state, stmt.line, `while condition false — exiting loop.`, 'control')
      return
    }
    snap(state, stmt.line, `while condition true — iteration ${iter} enters body.`, 'control')
    for (const s of stmt.body) execStmt(state, s)
    if (iter > 10000) throw new CRuntimeError('loop iteration limit exceeded (10000)', stmt.line)
  }
}

function execFor(state: State, stmt: {
  init: CVarDecl | CExpr | null
  condition: CExpr | null
  update: CExpr | null
  body: CStmt[]
  line: number
}): void {
  if (stmt.init) {
    if (isStmt(stmt.init)) execStmt(state, stmt.init as CStmt)
    else evalExpr(state, stmt.init as CExpr)
  }
  let iter = 0
  while (true) {
    iter++
    const condValue = stmt.condition ? evalExpr(state, stmt.condition) : { kind: 'int' as const, v: 1 }
    if (!truthy(condValue)) {
      snap(state, stmt.line, `for condition false — exiting loop after ${iter - 1} iteration${iter === 1 ? '' : 's'}.`, 'control')
      return
    }
    snap(state, stmt.line, `for iteration ${iter} enters body.`, 'control')
    for (const s of stmt.body) execStmt(state, s)
    if (stmt.update) evalExpr(state, stmt.update)
    if (iter > 10000) throw new CRuntimeError('loop iteration limit exceeded (10000)', stmt.line)
  }
}

class ReturnSignal {
  value: CValue | null
  line: number
  constructor(value: CValue | null, line: number) {
    this.value = value
    this.line = line
  }
}

function execReturn(state: State, stmt: { expr: CExpr | null; line: number }): void {
  const v = stmt.expr ? evalExpr(state, stmt.expr) : null
  throw new ReturnSignal(v, stmt.line)
}

function isStmt(node: unknown): boolean {
  if (typeof node !== 'object' || node === null) return false
  const k = (node as { kind?: string }).kind
  return k === 'varDecl' || k === 'assign'
}

// ---------------------------------------------------------------- expressions

function evalExpr(state: State, expr: CExpr): CValue {
  switch (expr.kind) {
    case 'intLit': return { kind: 'int', v: expr.v }
    case 'charLit': return { kind: 'char', v: expr.v }
    case 'strLit':
      // For now, treat string literals as a special pseudo-value used only
      // by printf. We don't allocate a heap block until we add real char*.
      // Caller (printf) inspects the AST kind, so this branch is mostly a
      // safety net.
      return { kind: 'int', v: 0 }
    case 'name': {
      const found = lookupBinding(state, expr.name)
      if (found === null) throw new CRuntimeError(`unknown variable '${expr.name}'`, expr.line)
      if (found.binding.value.kind === 'uninit') {
        throw new CRuntimeError(`reading uninitialized variable '${expr.name}'`, expr.line)
      }
      return cloneValue(found.binding.value)
    }
    case 'binop': return evalBinOp(state, expr)
    case 'cmp': return evalCmpOp(state, expr)
    case 'logical': return evalLogicalOp(state, expr)
    case 'not': {
      const v = evalExpr(state, expr.operand)
      return { kind: 'int', v: truthy(v) ? 0 : 1 }
    }
    case 'unop': {
      const v = evalExpr(state, expr.operand)
      const n = asInt(v, expr.line)
      return { kind: 'int', v: expr.op === '-' ? -n : n }
    }
    case 'call': return evalCall(state, expr)
    case 'sizeof': return { kind: 'int', v: sizeofType(expr.type) }
    case 'cast': return coerceToType(evalExpr(state, expr.expr), expr.type, expr.line)
    case 'assignExpr': {
      const target = lookupBinding(state, expr.target)
      if (target === null) throw new CRuntimeError(`unknown variable '${expr.target}'`, expr.line)
      const newValue = coerceToType(evalExpr(state, expr.value), target.binding.type, expr.line)
      target.binding.retired = true
      target.frame.bindings.push({
        name: expr.target, type: cloneType(target.binding.type), value: newValue, retired: false,
      })
      return newValue
    }
    case 'addrOf':
    case 'deref':
    case 'index':
      throw new CRuntimeError(`pointers/arrays are not supported in this MVP yet`, expr.line)
  }
}

function evalBinOp(state: State, expr: { op: '+' | '-' | '*' | '/' | '%'; left: CExpr; right: CExpr; line: number }): CValue {
  const l = asInt(evalExpr(state, expr.left), expr.line)
  const r = asInt(evalExpr(state, expr.right), expr.line)
  switch (expr.op) {
    case '+': return { kind: 'int', v: l + r }
    case '-': return { kind: 'int', v: l - r }
    case '*': return { kind: 'int', v: l * r }
    case '/':
      if (r === 0) throw new CRuntimeError(`division by zero`, expr.line)
      // C integer division truncates toward zero.
      return { kind: 'int', v: Math.trunc(l / r) }
    case '%':
      if (r === 0) throw new CRuntimeError(`modulo by zero`, expr.line)
      return { kind: 'int', v: l - Math.trunc(l / r) * r }
  }
}

function evalCmpOp(state: State, expr: { op: '==' | '!=' | '<' | '>' | '<=' | '>='; left: CExpr; right: CExpr; line: number }): CValue {
  const l = asInt(evalExpr(state, expr.left), expr.line)
  const r = asInt(evalExpr(state, expr.right), expr.line)
  let result: boolean
  switch (expr.op) {
    case '==': result = l === r; break
    case '!=': result = l !== r; break
    case '<': result = l < r; break
    case '>': result = l > r; break
    case '<=': result = l <= r; break
    case '>=': result = l >= r; break
  }
  return { kind: 'int', v: result ? 1 : 0 }
}

function evalLogicalOp(state: State, expr: { op: '&&' | '||'; left: CExpr; right: CExpr; line: number }): CValue {
  const l = evalExpr(state, expr.left)
  if (expr.op === '&&') {
    if (!truthy(l)) return { kind: 'int', v: 0 }
    return { kind: 'int', v: truthy(evalExpr(state, expr.right)) ? 1 : 0 }
  }
  if (truthy(l)) return { kind: 'int', v: 1 }
  return { kind: 'int', v: truthy(evalExpr(state, expr.right)) ? 1 : 0 }
}

function evalCall(state: State, expr: { callee: string; args: CExpr[]; line: number }): CValue {
  if (expr.callee === 'printf') {
    return execPrintf(state, expr)
  }
  if (expr.callee === 'malloc' || expr.callee === 'free') {
    throw new CRuntimeError(`malloc/free are not supported in this MVP yet`, expr.line)
  }
  const fn = state.functions.get(expr.callee)
  if (!fn) throw new CRuntimeError(`unknown function '${expr.callee}'`, expr.line)
  if (fn.params.length !== expr.args.length) {
    throw new CRuntimeError(
      `function '${expr.callee}' expects ${fn.params.length} arg(s), got ${expr.args.length}`,
      expr.line,
    )
  }
  const argValues = expr.args.map((a) => evalExpr(state, a))
  return callFunction(state, fn, argValues, expr.line) ?? { kind: 'int', v: 0 }
}

function callFunction(state: State, fn: CFunctionDef, args: CValue[], callerLine: number): CValue | null {
  const frame: CFrame = {
    name: fn.name,
    returnAddress: callerLine || null,
    returnValue: null,
    bindings: fn.params.map((p, i) => ({
      name: p.name,
      type: cloneType(p.type),
      value: coerceToType(args[i] ?? { kind: 'uninit' }, p.type, fn.lineStart),
      retired: false,
    })),
    retired: false,
  }
  state.stack.push(frame)
  snap(state, fn.lineStart, `Call ${fn.name}(${args.map(valueToDisplay).join(', ')}). New frame opens.`, 'call')

  let returnedValue: CValue | null = null
  try {
    for (const s of fn.body) execStmt(state, s)
  } catch (e) {
    if (e instanceof ReturnSignal) {
      returnedValue = e.value
    } else {
      throw e
    }
  }

  // Coerce return value to declared return type.
  if (fn.returnType.kind !== 'void' && returnedValue !== null) {
    returnedValue = coerceToType(returnedValue, fn.returnType, fn.lineEnd)
  }
  frame.returnValue = returnedValue
  frame.retired = true
  // Per memviz convention, we keep the frame visible (retired) instead of
  // popping it. New calls just push past it.
  snap(
    state,
    fn.lineEnd,
    `Return from ${fn.name}${returnedValue !== null ? ` with ${valueToDisplay(returnedValue)}` : ''}.`,
    'return',
  )
  return returnedValue
}

// printf is special: parses format string from the AST node directly so we
// can catch %d %c %s with type checking. Returns the number of chars
// printed (C semantics), but we just return 0 for simplicity.
function execPrintf(state: State, expr: { args: CExpr[]; line: number }): CValue {
  if (expr.args.length === 0) {
    throw new CRuntimeError(`printf requires a format string`, expr.line)
  }
  const fmtArg = expr.args[0]
  if (fmtArg.kind !== 'strLit') {
    throw new CRuntimeError(`printf format must be a string literal in this MVP`, expr.line)
  }
  const fmt = fmtArg.v
  const restArgs = expr.args.slice(1)
  let out = ''
  let argIdx = 0
  for (let i = 0; i < fmt.length; i++) {
    if (fmt[i] === '%' && i + 1 < fmt.length) {
      const spec = fmt[i + 1]
      i++
      if (spec === '%') { out += '%'; continue }
      const arg = restArgs[argIdx++]
      if (arg === undefined) {
        throw new CRuntimeError(`printf: format expects more args than provided`, expr.line)
      }
      if (spec === 'd') {
        const v = evalExpr(state, arg)
        out += String(asInt(v, expr.line))
      } else if (spec === 'c') {
        const v = evalExpr(state, arg)
        out += String.fromCharCode(asInt(v, expr.line) & 0xff)
      } else if (spec === 's') {
        // Only string literals supported for %s in this MVP.
        if (arg.kind !== 'strLit') {
          throw new CRuntimeError(`printf %s requires a string literal in this MVP`, expr.line)
        }
        out += arg.v
      } else {
        throw new CRuntimeError(`printf: unsupported format '%${spec}'`, expr.line)
      }
    } else {
      out += fmt[i]
    }
  }
  // C's printf doesn't auto-newline; we honor literal \n in the format.
  // Split on \n so each line becomes its own output line in the UI.
  const lines = out.split('\n')
  for (let li = 0; li < lines.length; li++) {
    if (li === lines.length - 1) {
      // last chunk after final \n: append to running buffer if non-empty.
      if (lines[li].length > 0) state.output.push(lines[li])
    } else {
      state.output.push(lines[li])
    }
  }
  snap(state, expr.line, `Printed: "${out.replace(/\n/g, '\\n')}".`, 'print')
  return { kind: 'int', v: out.length }
}

// ---------------------------------------------------------------- helpers

function topFrame(state: State): CFrame {
  for (let i = state.stack.length - 1; i >= 0; i--) {
    if (!state.stack[i].retired) return state.stack[i]
  }
  return state.stack[0]
}

function lookupBinding(state: State, name: string): { binding: CBinding; frame: CFrame } | null {
  // Walk from the top non-retired frame down to Globals, returning the
  // newest non-retired binding for that name.
  for (let i = state.stack.length - 1; i >= 0; i--) {
    const frame = state.stack[i]
    if (frame.retired) continue
    for (let j = frame.bindings.length - 1; j >= 0; j--) {
      const b = frame.bindings[j]
      if (b.name === name && !b.retired) return { binding: b, frame }
    }
  }
  // Fallback: search Globals (always frame 0) for non-retired bindings.
  const globals = state.stack[0]
  for (let j = globals.bindings.length - 1; j >= 0; j--) {
    const b = globals.bindings[j]
    if (b.name === name && !b.retired) return { binding: b, frame: globals }
  }
  return null
}

function asInt(v: CValue, line: number): number {
  if (v.kind === 'int') return v.v
  if (v.kind === 'char') return v.v
  if (v.kind === 'ptr') return v.address
  if (v.kind === 'uninit') throw new CRuntimeError(`reading uninitialized value`, line)
  throw new CRuntimeError(`expected an integer-like value`, line)
}

function truthy(v: CValue): boolean {
  if (v.kind === 'int' || v.kind === 'char') return v.v !== 0
  if (v.kind === 'ptr') return v.address !== 0
  return false
}

function coerceToType(v: CValue, target: CType, line: number): CValue {
  if (target.kind === 'int') {
    if (v.kind === 'int') return v
    if (v.kind === 'char') return { kind: 'int', v: v.v }
    if (v.kind === 'uninit') return v
    throw new CRuntimeError(`cannot convert ${v.kind} to int`, line)
  }
  if (target.kind === 'char') {
    if (v.kind === 'char') return v
    if (v.kind === 'int') return { kind: 'char', v: v.v & 0xff }
    if (v.kind === 'uninit') return v
    throw new CRuntimeError(`cannot convert ${v.kind} to char`, line)
  }
  if (target.kind === 'void') return v
  // ptr / arr — pass through; pointer support arrives in next iteration.
  return v
}

function sizeofType(t: CType): number {
  switch (t.kind) {
    case 'int': return 4
    case 'char': return 1
    case 'void': return 1 // gcc-ism; technically illegal
    case 'ptr': return 8
    case 'arr': return sizeofType(t.of) * t.length
  }
}

function typeToStr(t: CType): string {
  switch (t.kind) {
    case 'int': return 'int'
    case 'char': return 'char'
    case 'void': return 'void'
    case 'ptr': return typeToStr(t.to) + '*'
    case 'arr': return `${typeToStr(t.of)}[${t.length}]`
  }
}

function valueToDisplay(v: CValue): string {
  switch (v.kind) {
    case 'int': return String(v.v)
    case 'char': return `'${String.fromCharCode(v.v)}' (${v.v})`
    case 'ptr': return v.address === 0 ? 'NULL' : `0x${v.address.toString(16)}`
    case 'uninit': return '?'
  }
}
