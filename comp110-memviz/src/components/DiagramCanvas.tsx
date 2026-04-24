import type { ReactNode } from 'react'
import type { Frame, HeapObject, Snapshot, Value } from '../interpreter/types'
import './DiagramCanvas.css'

type Props = {
  snapshot: Snapshot | null
}

export function DiagramCanvas({ snapshot }: Props) {
  if (!snapshot) {
    return (
      <div className="diagram placeholder">
        <p>Write some code and press <strong>Run</strong> to see the diagram.</p>
      </div>
    )
  }

  // The active frame is the last non-retired, non-Globals frame. It's the one
  // currently executing — highlight it yellow.
  let activeIdx = -1
  for (let i = snapshot.stack.length - 1; i >= 0; i--) {
    const f = snapshot.stack[i]
    if (!f.retired && f.name !== 'Globals') {
      activeIdx = i
      break
    }
  }

  return (
    <div className="diagram">
      <section className="col stack">
        <header className="col-title">Function Call Stack</header>
        <div className="frames">
          {/* COMP110 convention: Globals is drawn at the TOP (first written);
              each new call frame is added below it in chronological order. */}
          {snapshot.stack.map((frame, idx) => (
            <FrameView
              key={idx}
              frame={frame}
              heap={snapshot.heap}
              isActive={idx === activeIdx}
            />
          ))}
        </div>
      </section>

      <section className="col heap">
        <header className="col-title">Heap</header>
        <div className="heap-objects">
          {snapshot.heap.length === 0 && <p className="empty">(no heap objects yet)</p>}
          {snapshot.heap.map((h) => (
            <HeapObjectView key={h.id} obj={h} />
          ))}
        </div>
      </section>

      <section className="col output">
        <header className="col-title">Printed Output</header>
        <div className="output-lines">
          {snapshot.output.length === 0 && <p className="empty">(nothing printed yet)</p>}
          {snapshot.output.map((line, i) => (
            <div key={i} className="output-line">{line}</div>
          ))}
        </div>
      </section>
    </div>
  )
}

function FrameView({ frame, heap, isActive }: { frame: Frame; heap: HeapObject[]; isActive: boolean }) {
  const cls = [
    'frame',
    isActive ? 'active' : '',
    frame.name === 'Globals' ? 'globals' : '',
    frame.retired ? 'retired' : '',
  ]
    .filter(Boolean)
    .join(' ')
  return (
    <div className={cls}>
      <div className="frame-header">
        <span className="frame-name">{frame.name}</span>
        {frame.returnAddress !== null && <span className="ra">RA: {frame.returnAddress}</span>}
        {frame.returnValue !== null && (
          <span className="rv">RV: {formatValue(frame.returnValue, heap)}</span>
        )}
      </div>
      <div className="bindings">
        {frame.bindings.length === 0 && (
          <div className="binding empty-binding">(empty)</div>
        )}
        {groupByName(frame.bindings).map((g, i) => (
          <div key={i} className="binding">
            <span className="name">{g.name}</span>
            <span className="eq">=</span>
            <span className="value">
              {renderHistory(g.items.map((b) => ({ retired: b.retired, text: formatValue(b.value, heap) })))}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Group an append-only Binding[] by name, preserving first-seen order.
// Every group holds the full history; renderHistory then emits chunks for
// each retired entry plus the final active entry — all on the same row.
function groupByName<T extends { name: string; retired: boolean }>(arr: T[]): { name: string; items: T[] }[] {
  const firstIdx = new Map<string, number>()
  arr.forEach((b, i) => {
    if (!firstIdx.has(b.name)) firstIdx.set(b.name, i)
  })
  const groups = new Map<string, T[]>()
  for (const b of arr) {
    const existing = groups.get(b.name)
    if (existing) existing.push(b)
    else groups.set(b.name, [b])
  }
  return [...firstIdx.entries()]
    .sort((a, b) => a[1] - b[1])
    .map(([name]) => ({ name, items: groups.get(name)! }))
    // Drop groups with no active entry (e.g. a list slot after pop removed
    // the last one). They no longer "exist" in Python semantics.
    .filter((g) => g.items.some((b) => !b.retired))
}

// Given a chronological list of versions for one slot, render them inline:
// each retired version gets a struck-through chunk, then the one active
// version appears as normal text at the end. Whitespace between chunks is
// a single space so visually they read as "old new".
function renderHistory(versions: { retired: boolean; text: string }[]): ReactNode {
  return versions.map((v, i) => (
    <span
      key={i}
      className={v.retired ? 'chunk retired' : 'chunk active'}
    >
      {v.text}
      {i < versions.length - 1 ? ' ' : ''}
    </span>
  ))
}

function HeapObjectView({ obj }: { obj: HeapObject }) {
  if (obj.kind === 'function') {
    return (
      <div className="heap-obj function">
        <span className="heap-id">ID:{obj.id}</span>
        <span className="heap-label">function lines {obj.lineStart}–{obj.lineEnd}</span>
        <span className="heap-name">{obj.name}</span>
      </div>
    )
  }
  if (obj.kind === 'class') {
    return (
      <div className="heap-obj class">
        <span className="heap-id">ID:{obj.id}</span>
        <span className="heap-label">class lines {obj.lineStart}–{obj.lineEnd}</span>
        <span className="heap-name">{obj.name}</span>
      </div>
    )
  }
  if (obj.kind === 'list') {
    // Group slots by index; only active index groups remain.
    const slotGroups = groupByIndex(obj.slots)
    return (
      <div className="heap-obj list">
        <div className="heap-obj-header">
          <span className="heap-id">ID:{obj.id}</span>
          <span className="heap-label">list</span>
        </div>
        <div className="bindings list-slots">
          {slotGroups.length === 0 && <div className="binding empty-binding">(empty)</div>}
          {slotGroups.map((g, i) => (
            <div key={i} className="binding">
              <span className="name">[{g.index}]</span>
              <span className="eq">=</span>
              <span className="value">
                {renderHistory(g.items.map((s) => ({ retired: s.retired, text: formatValueSimple(s.value) })))}
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }
  if (obj.kind === 'dict') {
    // Group by stringified key (the binding's `name` field).
    const entryGroups = groupByName(obj.entries)
    return (
      <div className="heap-obj dict">
        <div className="heap-obj-header">
          <span className="heap-id">ID:{obj.id}</span>
          <span className="heap-label">dict</span>
        </div>
        <div className="bindings dict-entries">
          {entryGroups.length === 0 && <div className="binding empty-binding">(empty)</div>}
          {entryGroups.map((g, i) => (
            <div key={i} className="binding">
              <span className="name">{formatDictKey(g.name)}</span>
              <span className="eq">:</span>
              <span className="value">
                {renderHistory(g.items.map((e) => ({ retired: e.retired, text: formatValueSimple(e.value) })))}
              </span>
            </div>
          ))}
        </div>
      </div>
    )
  }
  // instance
  const attrGroups = groupByName(obj.attrs)
  return (
    <div className="heap-obj instance">
      <div className="heap-obj-header">
        <span className="heap-id">ID:{obj.id}</span>
        <span className="heap-label">{obj.className}</span>
      </div>
      <div className="bindings instance-attrs">
        {attrGroups.length === 0 && <div className="binding empty-binding">(no attrs)</div>}
        {attrGroups.map((g, i) => (
          <div key={i} className="binding">
            <span className="name">{g.name}</span>
            <span className="eq">=</span>
            <span className="value">
              {renderHistory(g.items.map((b) => ({ retired: b.retired, text: formatValueSimple(b.value) })))}
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

// Same as groupByName but keyed by numeric `index` (used for list slots).
function groupByIndex<T extends { index: number; retired: boolean }>(arr: T[]): { index: number; items: T[] }[] {
  const firstIdx = new Map<number, number>()
  arr.forEach((s, i) => {
    if (!firstIdx.has(s.index)) firstIdx.set(s.index, i)
  })
  const groups = new Map<number, T[]>()
  for (const s of arr) {
    const existing = groups.get(s.index)
    if (existing) existing.push(s)
    else groups.set(s.index, [s])
  }
  return [...firstIdx.entries()]
    .sort((a, b) => a[1] - b[1])
    .map(([index]) => ({ index, items: groups.get(index)! }))
    .filter((g) => g.items.some((s) => !s.retired))
}

function formatValue(v: Value, heap: HeapObject[]): string {
  switch (v.kind) {
    case 'int': return String(v.v)
    case 'float': return Number.isInteger(v.v) ? `${v.v}.0` : String(v.v)
    case 'str': return JSON.stringify(v.v)
    case 'bool': return v.v ? 'True' : 'False'
    case 'none': return 'None'
    case 'ref': {
      const h = heap.find((x) => x.id === v.id)
      if (!h) return `→ ID:${v.id} (missing)`
      return `→ ID:${v.id}`
    }
  }
}

// Dict keys are stored as stringified values prefixed with a type tag.
function formatDictKey(tagged: string): string {
  const tag = tagged[0]
  const rest = tagged.slice(2)
  if (tag === 'S') return `'${rest}'`
  if (tag === 'I' || tag === 'F') return rest
  if (tag === 'B') return rest === '1' ? 'True' : 'False'
  if (tag === 'N') return 'None'
  if (tag === 'R') return `→ ID:${rest}`
  return tagged
}

function formatValueSimple(v: Value): string {
  switch (v.kind) {
    case 'int': return String(v.v)
    case 'float': return Number.isInteger(v.v) ? `${v.v}.0` : String(v.v)
    case 'str': return JSON.stringify(v.v)
    case 'bool': return v.v ? 'True' : 'False'
    case 'none': return 'None'
    case 'ref': return `→ ID:${v.id}`
  }
}
