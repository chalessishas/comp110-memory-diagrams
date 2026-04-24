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
  ClassDef,
  Expr,
  FunctionDef,
  Frame,
  HeapInstance,
  HeapList,
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
  classDefs: Map<string, ClassDef>
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

function cloneHeapObject(h: HeapObject): HeapObject {
  if (h.kind === 'instance') {
    return {
      id: h.id,
      kind: 'instance',
      className: h.className,
      classId: h.classId,
      // Deep-clone attrs so retired flags at the time of the snapshot are frozen.
      attrs: h.attrs.map((b) => ({
        name: b.name,
        value: cloneValue(b.value),
        retired: b.retired,
      })),
    }
  }
  if (h.kind === 'class') {
    return { ...h, methodNames: [...h.methodNames] }
  }
  if (h.kind === 'list') {
    return {
      id: h.id,
      kind: 'list',
      elementType: h.elementType,
      slots: h.slots.map((s) => ({
        index: s.index,
        value: cloneValue(s.value),
        retired: s.retired,
      })),
    }
  }
  return { ...h }
}

// ----- List helpers (v2) ------------------------------------------------

function listLength(lst: HeapList): number {
  // Distinct non-retired slot indexes = current logical length.
  const seen = new Set<number>()
  for (const s of lst.slots) {
    if (!s.retired) seen.add(s.index)
  }
  return seen.size
}

function listGet(lst: HeapList, index: number): Value | undefined {
  for (let i = lst.slots.length - 1; i >= 0; i--) {
    const s = lst.slots[i]
    if (!s.retired && s.index === index) return s.value
  }
  return undefined
}

function listSet(lst: HeapList, index: number, value: Value) {
  for (const s of lst.slots) {
    if (!s.retired && s.index === index) s.retired = true
  }
  lst.slots.push({ index, value, retired: false })
}

function listAppend(lst: HeapList, value: Value) {
  lst.slots.push({ index: listLength(lst), value, retired: false })
}

function snap(state: State, currentLine: number, narration: string, error: string | null = null): Snapshot {
  return {
    step: state.snapshots.length,
    currentLine,
    narration,
    stack: state.stack.map(cloneFrame),
    heap: state.heap.map(cloneHeapObject),
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

// Python-like truthiness. v1 truthiness rules: None/False/0/""/0.0 → false.
function truthy(v: Value): boolean {
  if (v.kind === 'none') return false
  if (v.kind === 'bool') return v.v
  if (v.kind === 'int' || v.kind === 'float') return v.v !== 0
  if (v.kind === 'str') return v.v.length > 0
  return true // refs are always truthy
}

function lookupAttr(inst: HeapInstance, attr: string): Value | undefined {
  for (let i = inst.attrs.length - 1; i >= 0; i--) {
    const b = inst.attrs[i]
    if (!b.retired && b.name === attr) return b.value
  }
  return undefined
}

function setAttr(inst: HeapInstance, attr: string, value: Value) {
  for (const b of inst.attrs) {
    if (!b.retired && b.name === attr) b.retired = true
  }
  inst.attrs.push({ name: attr, value, retired: false })
}

function valueToDisplay(v: Value, state: State): string {
  if (v.kind === 'int') return String(v.v)
  if (v.kind === 'float') return Number.isInteger(v.v) ? `${v.v}.0` : String(v.v)
  if (v.kind === 'str') return v.v
  if (v.kind === 'bool') return v.v ? 'True' : 'False'
  if (v.kind === 'none') return 'None'
  if (v.kind === 'ref') {
    const obj = state.heap.find((h) => h.id === v.id)
    if (!obj) return `ID:${v.id}`
    if (obj.kind === 'instance') return `ID:${v.id} (${obj.className})`
    if (obj.kind === 'list') return `ID:${v.id} (list)`
    return `ID:${v.id} (${obj.name})`
  }
  return '?'
}

// Python-style list repr. Used by print(list) and f-string interpolation of
// lists. Strings are quoted, other values use valueToDisplay.
function listRepr(lst: HeapList, state: State): string {
  const len = listLength(lst)
  const items: string[] = []
  for (let i = 0; i < len; i++) {
    const v = listGet(lst, i)
    if (v === undefined) { items.push('?'); continue }
    if (v.kind === 'str') items.push(`'${v.v}'`)
    else items.push(valueToDisplay(v, state))
  }
  return '[' + items.join(', ') + ']'
}

function evalExpr(state: State, expr: Expr): Value {
  switch (expr.kind) {
    case 'num':
      return expr.isFloat ? { kind: 'float', v: expr.v } : { kind: 'int', v: expr.v }
    case 'str':
      return { kind: 'str', v: expr.v }
    case 'bool':
      return { kind: 'bool', v: expr.v }
    case 'fstr': {
      let out = ''
      for (const p of expr.parts) {
        if (p.kind === 'lit') out += p.v
        else out += toStr(state, evalExpr(state, p.expr), expr.line)
      }
      return { kind: 'str', v: out }
    }
    case 'cmp': {
      const l = evalExpr(state, expr.left)
      const r = evalExpr(state, expr.right)
      return { kind: 'bool', v: compareValues(l, r, expr.op, expr.line) }
    }
    case 'boolOp': {
      const l = evalExpr(state, expr.left)
      // Python short-circuit: returns the last-evaluated value, not a bool.
      // For simplicity in v1 we return a bool because that matches student
      // intuition in if-conditions.
      if (expr.op === 'and') {
        if (!truthy(l)) return { kind: 'bool', v: false }
        return { kind: 'bool', v: truthy(evalExpr(state, expr.right)) }
      } else {
        if (truthy(l)) return { kind: 'bool', v: true }
        return { kind: 'bool', v: truthy(evalExpr(state, expr.right)) }
      }
    }
    case 'not': {
      const v = evalExpr(state, expr.operand)
      return { kind: 'bool', v: !truthy(v) }
    }
    case 'attr': {
      const target = evalExpr(state, expr.target)
      if (target.kind !== 'ref') {
        throw new RuntimeErrorSignal(
          `AttributeError on line ${expr.line}: cannot read '.${expr.name}' on non-object`,
          expr.line,
        )
      }
      const obj = state.heap.find((h) => h.id === target.id)
      if (!obj || obj.kind !== 'instance') {
        throw new RuntimeErrorSignal(
          `AttributeError on line ${expr.line}: '${expr.name}' on non-instance`,
          expr.line,
        )
      }
      const v = lookupAttr(obj, expr.name)
      if (v === undefined) {
        throw new RuntimeErrorSignal(
          `AttributeError on line ${expr.line}: '${obj.className}' object has no attribute '${expr.name}'`,
          expr.line,
        )
      }
      return v
    }
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
      if (idx.kind !== 'int') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${expr.line}: index must be int`,
          expr.line,
        )
      }
      // String indexing (v0).
      if (target.kind === 'str') {
        const i = idx.v < 0 ? target.v.length + idx.v : idx.v
        if (i < 0 || i >= target.v.length) {
          throw new RuntimeErrorSignal(
            `IndexError on line ${expr.line}: string index ${idx.v} out of range`,
            expr.line,
          )
        }
        return { kind: 'str', v: target.v[i] }
      }
      // List indexing (v2).
      if (target.kind === 'ref') {
        const obj = state.heap.find((h) => h.id === target.id)
        if (obj && obj.kind === 'list') {
          const len = listLength(obj)
          const i = idx.v < 0 ? len + idx.v : idx.v
          if (i < 0 || i >= len) {
            throw new RuntimeErrorSignal(
              `IndexError on line ${expr.line}: list index ${idx.v} out of range (len=${len})`,
              expr.line,
            )
          }
          const v = listGet(obj, i)
          if (v === undefined) {
            throw new RuntimeErrorSignal(
              `IndexError on line ${expr.line}: list slot ${i} missing`,
              expr.line,
            )
          }
          return v
        }
      }
      throw new RuntimeErrorSignal(
        `TypeError on line ${expr.line}: cannot index ${target.kind}`,
        expr.line,
      )
    }
    case 'listLit': {
      const id = state.nextHeapId++
      const lst: HeapList = {
        id,
        kind: 'list',
        elementType: 'Any',
        slots: [],
      }
      state.heap.push(lst)
      for (const el of expr.elements) {
        const v = evalExpr(state, el)
        listAppend(lst, v)
      }
      push(
        state,
        snap(
          state,
          expr.line,
          `Created list ID:${id} with ${expr.elements.length} initial element(s).`,
        ),
      )
      return { kind: 'ref', id }
    }
  }
}

function compareValues(l: Value, r: Value, op: string, line: number): boolean {
  // Normalize booleans to 0/1 for numeric comparisons so `True == 1` behaves
  // the way Python does.
  const toNum = (v: Value): number | null => {
    if (v.kind === 'int' || v.kind === 'float') return v.v
    if (v.kind === 'bool') return v.v ? 1 : 0
    return null
  }
  if (l.kind === 'none' || r.kind === 'none') {
    // Only == / != make sense; both must be none for equality.
    if (op === '==') return l.kind === 'none' && r.kind === 'none'
    if (op === '!=') return !(l.kind === 'none' && r.kind === 'none')
    throw new RuntimeErrorSignal(`TypeError on line ${line}: cannot ${op} with None`, line)
  }
  if (l.kind === 'str' && r.kind === 'str') {
    switch (op) {
      case '==': return l.v === r.v
      case '!=': return l.v !== r.v
      case '<': return l.v < r.v
      case '>': return l.v > r.v
      case '<=': return l.v <= r.v
      case '>=': return l.v >= r.v
    }
  }
  if (l.kind === 'ref' && r.kind === 'ref') {
    if (op === '==') return l.id === r.id
    if (op === '!=') return l.id !== r.id
    throw new RuntimeErrorSignal(`TypeError on line ${line}: cannot ${op} objects`, line)
  }
  const ln = toNum(l)
  const rn = toNum(r)
  if (ln === null || rn === null) {
    throw new RuntimeErrorSignal(
      `TypeError on line ${line}: cannot ${op} ${l.kind} and ${r.kind}`,
      line,
    )
  }
  switch (op) {
    case '==': return ln === rn
    case '!=': return ln !== rn
    case '<': return ln < rn
    case '>': return ln > rn
    case '<=': return ln <= rn
    case '>=': return ln >= rn
  }
  throw new RuntimeErrorSignal(`unknown comparison '${op}'`, line)
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
  // 1) Method call: `obj.method(args)` → self = obj, look up method on obj's class.
  if (expr.methodOf) {
    const selfVal = evalExpr(state, expr.methodOf)
    if (selfVal.kind !== 'ref') {
      throw new RuntimeErrorSignal(
        `TypeError on line ${expr.line}: '.${expr.callee}' on non-object`,
        expr.line,
      )
    }
    const obj = state.heap.find((h) => h.id === selfVal.id)
    // List methods — v2 supports .append(value).
    if (obj && obj.kind === 'list') {
      if (expr.callee === 'append') {
        if (expr.args.length !== 1) {
          throw new RuntimeErrorSignal(
            `Function Call Error on Line ${expr.line}: list.append takes exactly 1 arg`,
            expr.line,
          )
        }
        const v = evalExpr(state, expr.args[0].value)
        listAppend(obj, v)
        push(
          state,
          snap(
            state,
            expr.line,
            `Appended ${valueToDisplay(v, state)} to list ID:${obj.id} (now length ${listLength(obj)}).`,
          ),
        )
        return { kind: 'none' }
      }
      throw new RuntimeErrorSignal(
        `AttributeError on line ${expr.line}: 'list' has no method '${expr.callee}' (v2 only supports append)`,
        expr.line,
      )
    }
    if (!obj || obj.kind !== 'instance') {
      throw new RuntimeErrorSignal(
        `AttributeError on line ${expr.line}: '.${expr.callee}' on non-instance`,
        expr.line,
      )
    }
    const cls = state.classDefs.get(obj.className)
    if (!cls) {
      throw new RuntimeErrorSignal(
        `NameError on line ${expr.line}: class '${obj.className}' not defined`,
        expr.line,
      )
    }
    const method = cls.methods.find((m) => m.name === expr.callee)
    if (!method) {
      throw new RuntimeErrorSignal(
        `AttributeError on line ${expr.line}: '${obj.className}' has no method '${expr.callee}'`,
        expr.line,
      )
    }
    const argValues = expr.args.map((a) => ({ name: a.name, value: evalExpr(state, a.value) }))
    return callUserFunction(state, method, argValues, expr.line, selfVal, `${obj.className}.${expr.callee}`)
  }

  // Evaluate args left-to-right.
  const argValues = expr.args.map((a) => ({ name: a.name, value: evalExpr(state, a.value) }))

  // Built-ins: no stack frame created.
  if (BUILTINS.has(expr.callee)) {
    return applyBuiltin(state, expr, argValues)
  }

  // Resolve the name in current/global frame.
  const ref = resolveName(state, expr.callee, expr.line)
  if (ref.kind !== 'ref') {
    throw new RuntimeErrorSignal(
      `TypeError on line ${expr.line}: '${expr.callee}' is not callable`,
      expr.line,
    )
  }

  // 2) Class instantiation: callee is a class name.
  const cls = state.classDefs.get(expr.callee)
  if (cls) {
    return instantiateClass(state, cls, argValues, expr.line)
  }

  // 3) Regular user function call.
  const fn = state.funcDefs.get(expr.callee)
  if (!fn) {
    throw new RuntimeErrorSignal(
      `NameError on line ${expr.line}: '${expr.callee}' not callable`,
      expr.line,
    )
  }
  return callUserFunction(state, fn, argValues, expr.line, null, expr.callee)
}

// Create an instance on the heap, invoke __init__ (if any), return the ref.
function instantiateClass(
  state: State,
  cls: ClassDef,
  argValues: { name: string | null; value: Value }[],
  line: number,
): Value {
  const id = state.nextHeapId++
  const instance: HeapInstance = {
    id,
    kind: 'instance',
    className: cls.name,
    classId: id, // not strictly the class's id — we look up by name, this field is for future
    attrs: [],
  }
  state.heap.push(instance)
  const selfRef: Value = { kind: 'ref', id }
  push(
    state,
    snap(
      state,
      line,
      `Instantiated ${cls.name}. New heap instance ID:${id} created (empty attrs).`,
    ),
  )
  const init = cls.methods.find((m) => m.name === '__init__')
  if (init) {
    callUserFunction(state, init, argValues, line, selfRef, `${cls.name}.__init__`)
  } else if (argValues.length > 0) {
    throw new RuntimeErrorSignal(
      `Function Call Error on Line ${line}: ${cls.name}() takes no arguments (no __init__ defined)`,
      line,
    )
  }
  return selfRef
}

// Push a frame, bind params, run the body, retire the frame, return RV.
// selfValue is injected as the first parameter when present (method calls).
function callUserFunction(
  state: State,
  fn: FunctionDef,
  argValues: { name: string | null; value: Value }[],
  callLine: number,
  selfValue: Value | null,
  displayName: string,
): Value {
  // When selfValue is provided, the method's first declared param is `self`
  // and it is filled from selfValue rather than argValues.
  const params = fn.params
  let paramsToFill = params
  const preBindings: Binding[] = []
  if (selfValue) {
    if (params.length === 0 || params[0].name !== 'self') {
      throw new RuntimeErrorSignal(
        `SyntaxError on line ${callLine}: method '${fn.name}' must declare 'self' as its first parameter`,
        callLine,
      )
    }
    preBindings.push({ name: 'self', value: selfValue, retired: false })
    paramsToFill = params.slice(1)
  }

  if (argValues.length !== paramsToFill.length) {
    throw new RuntimeErrorSignal(
      `Function Call Error on Line ${callLine}: ${displayName} expects ${paramsToFill.length} arg(s), got ${argValues.length}`,
      callLine,
    )
  }
  const paramValues: Record<string, Value> = {}
  const used = new Set<string>()
  for (let i = 0; i < argValues.length; i++) {
    const { name, value } = argValues[i]
    if (name !== null) {
      const p = paramsToFill.find((p) => p.name === name)
      if (!p) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${callLine}: unknown keyword '${name}' for ${displayName}`,
          callLine,
        )
      }
      if (used.has(name)) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${callLine}: duplicate keyword '${name}'`,
          callLine,
        )
      }
      used.add(name)
      paramValues[name] = value
    } else {
      const p = paramsToFill[i]
      if (!p || used.has(p.name)) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${callLine}: too many positional args for ${displayName}`,
          callLine,
        )
      }
      used.add(p.name)
      paramValues[p.name] = value
    }
  }
  for (const p of paramsToFill) {
    if (!(p.name in paramValues)) {
      throw new RuntimeErrorSignal(
        `Function Call Error on Line ${callLine}: missing argument '${p.name}' for ${displayName}`,
        callLine,
      )
    }
  }

  const bindings: Binding[] = [
    ...preBindings,
    ...paramsToFill.map((p) => ({ name: p.name, value: paramValues[p.name], retired: false })),
  ]

  const newFrame: Frame = {
    name: displayName,
    returnAddress: callLine,
    returnValue: null,
    bindings,
    retired: false,
  }
  state.stack.push(newFrame)
  const argsList = paramsToFill
    .map((p) => `${p.name}=${valueToDisplay(paramValues[p.name], state)}`)
    .join(', ')
  const selfDesc = selfValue ? `self=${valueToDisplay(selfValue, state)}${argsList ? ', ' : ''}` : ''
  push(
    state,
    snap(
      state,
      fn.lineStart,
      `Call ${displayName}(${selfDesc}${argsList}). New frame pushed; jumping to line ${fn.lineStart}.`,
    ),
  )

  let rv: Value = { kind: 'none' }
  try {
    for (const stmt of fn.body) execStmt(state, stmt)
  } catch (e) {
    if (e instanceof ReturnSignal) rv = e.value
    else throw e
  }

  newFrame.returnValue = rv
  newFrame.retired = true
  push(
    state,
    snap(
      state,
      newFrame.returnAddress ?? fn.lineEnd,
      `Return from ${displayName} with RV = ${valueToDisplay(rv, state)}. Frame retired (struck through). Jumping back to line ${newFrame.returnAddress}.`,
    ),
  )
  return rv
}

// Convert any Value into a displayable string, invoking __str__ on instances
// when the class defines one. This mirrors Python's str(obj) behavior and is
// what print, str(), and f-string interpolation all route through.
function toStr(state: State, v: Value, callLine: number): string {
  if (v.kind === 'ref') {
    const obj = state.heap.find((h) => h.id === v.id)
    if (obj && obj.kind === 'list') return listRepr(obj, state)
    if (obj && obj.kind === 'instance') {
      const cls = state.classDefs.get(obj.className)
      const dunder = cls?.methods.find((m) => m.name === '__str__')
      if (cls && dunder) {
        const result = callUserFunction(state, dunder, [], callLine, v, `${cls.name}.__str__`)
        if (result.kind === 'str') return result.v
        return valueToDisplay(result, state)
      }
    }
  }
  return valueToDisplay(v, state)
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
      const line = toStr(state, values[0], expr.line)
      state.output.push(line)
      push(state, snap(state, expr.line, `Printed '${line}' to Output.`))
      return { kind: 'none' }
    }
    case 'len': {
      if (values.length !== 1) {
        throw new RuntimeErrorSignal(
          `Function Call Error on Line ${expr.line}: len() expects one argument`,
          expr.line,
        )
      }
      const arg = values[0]
      if (arg.kind === 'str') return { kind: 'int', v: arg.v.length }
      if (arg.kind === 'ref') {
        const obj = state.heap.find((h) => h.id === arg.id)
        if (obj && obj.kind === 'list') return { kind: 'int', v: listLength(obj) }
      }
      throw new RuntimeErrorSignal(
        `Function Call Error on Line ${expr.line}: len() supports string or list`,
        expr.line,
      )
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
      return { kind: 'str', v: toStr(state, values[0], expr.line) }
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
    case 'assign': {
      const v = evalExpr(state, stmt.value)
      const frame = currentFrame(state)
      // setBinding retires any existing active binding with this name and
      // pushes a new one — exactly the v0 rule for reassignment.
      setBinding(frame, stmt.target, v)
      const isRebind = frame.bindings.some(
        (b) => b.retired && b.name === stmt.target,
      )
      const verb = stmt.typeAnnotation !== null
        ? `Declared ${stmt.target}: ${stmt.typeAnnotation}`
        : isRebind
          ? `Reassigned ${stmt.target} (old value struck through)`
          : `Assigned ${stmt.target}`
      push(state, snap(state, stmt.line, `${verb} = ${valueToDisplay(v, state)}.`))
      return
    }
    case 'attrAssign': {
      const targetVal = evalExpr(state, stmt.target)
      if (targetVal.kind !== 'ref') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${stmt.line}: cannot assign attribute on non-object`,
          stmt.line,
        )
      }
      const obj = state.heap.find((h) => h.id === targetVal.id)
      if (!obj || obj.kind !== 'instance') {
        throw new RuntimeErrorSignal(
          `AttributeError on line ${stmt.line}: assignment on non-instance`,
          stmt.line,
        )
      }
      const v = evalExpr(state, stmt.value)
      const hadPrior = obj.attrs.some((b) => !b.retired && b.name === stmt.attr)
      setAttr(obj, stmt.attr, v)
      const verb = hadPrior ? 'Reassigned' : 'Set'
      push(
        state,
        snap(
          state,
          stmt.line,
          `${verb} ${obj.className} ID:${obj.id}.${stmt.attr} = ${valueToDisplay(v, state)}${hadPrior ? ' (old value struck through)' : ''}.`,
        ),
      )
      return
    }
    case 'if': {
      for (const br of stmt.branches) {
        const cond = evalExpr(state, br.condition)
        if (truthy(cond)) {
          push(state, snap(state, stmt.line, `Condition true — entering if/elif branch on line ${stmt.line}.`))
          for (const s of br.body) execStmt(state, s)
          return
        }
      }
      if (stmt.elseBody) {
        push(state, snap(state, stmt.line, `All conditions false — entering else branch on line ${stmt.line}.`))
        for (const s of stmt.elseBody) execStmt(state, s)
      } else {
        push(state, snap(state, stmt.line, `All conditions false — skipping if on line ${stmt.line}.`))
      }
      return
    }
    case 'while': {
      const MAX_ITERS = 10000
      let iter = 0
      while (iter++ < MAX_ITERS) {
        const cond = evalExpr(state, stmt.condition)
        if (!truthy(cond)) {
          push(state, snap(state, stmt.line, `while condition false — exiting loop on line ${stmt.line}.`))
          return
        }
        push(state, snap(state, stmt.line, `while condition true — iteration ${iter} enters body.`))
        for (const s of stmt.body) execStmt(state, s)
      }
      throw new RuntimeErrorSignal(
        `RuntimeError on line ${stmt.line}: while loop exceeded ${MAX_ITERS} iterations (suspected infinite loop)`,
        stmt.line,
      )
    }
    case 'indexAssign': {
      const targetVal = evalExpr(state, stmt.target)
      if (targetVal.kind !== 'ref') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${stmt.line}: cannot index-assign on non-object`,
          stmt.line,
        )
      }
      const obj = state.heap.find((h) => h.id === targetVal.id)
      if (!obj || obj.kind !== 'list') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${stmt.line}: index-assign only supported on lists`,
          stmt.line,
        )
      }
      const idxVal = evalExpr(state, stmt.index)
      if (idxVal.kind !== 'int') {
        throw new RuntimeErrorSignal(
          `TypeError on line ${stmt.line}: list index must be int`,
          stmt.line,
        )
      }
      const len = listLength(obj)
      const i = idxVal.v < 0 ? len + idxVal.v : idxVal.v
      if (i < 0 || i >= len) {
        throw new RuntimeErrorSignal(
          `IndexError on line ${stmt.line}: list index ${idxVal.v} out of range (len=${len})`,
          stmt.line,
        )
      }
      const newVal = evalExpr(state, stmt.value)
      listSet(obj, i, newVal)
      push(
        state,
        snap(
          state,
          stmt.line,
          `Reassigned list ID:${obj.id}[${i}] = ${valueToDisplay(newVal, state)} (old value struck through).`,
        ),
      )
      return
    }
    case 'classDef': {
      addClassDef(state, stmt)
      return
    }
  }
}

function addClassDef(state: State, cls: ClassDef) {
  state.classDefs.set(cls.name, cls)
  const id = state.nextHeapId++
  state.heap.push({
    id,
    kind: 'class',
    name: cls.name,
    lineStart: cls.lineStart,
    lineEnd: cls.lineEnd,
    methodNames: cls.methods.map((m) => m.name),
  })
  const frame = currentFrame(state)
  setBinding(frame, cls.name, { kind: 'ref', id })
  push(
    state,
    snap(
      state,
      cls.lineStart,
      `Defined class '${cls.name}' (lines ${cls.lineStart}-${cls.lineEnd}) with methods [${cls.methods.map((m) => m.name).join(', ')}]. Heap ID:${id} created; '${cls.name}' bound in current frame.`,
    ),
  )
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
    classDefs: new Map(),
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
