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
        {frame.bindings.map((b, i) => (
          <div key={i} className={`binding${b.retired ? ' retired' : ''}`}>
            <span className="name">{b.name}</span>
            <span className="eq">=</span>
            <span className="value">{formatValue(b.value, heap)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function HeapObjectView({ obj }: { obj: HeapObject }) {
  if (obj.kind === 'function') {
    return (
      <div className="heap-obj function">
        <span className="heap-id">ID:{obj.id}</span>
        <span className="heap-label">Fn Lines {obj.lineStart}–{obj.lineEnd}</span>
        <span className="heap-name">({obj.name})</span>
      </div>
    )
  }
  if (obj.kind === 'class') {
    return (
      <div className="heap-obj class">
        <span className="heap-id">ID:{obj.id}</span>
        <span className="heap-label">class {obj.name}</span>
        <span className="heap-name">methods: {obj.methodNames.join(', ') || '(none)'}</span>
      </div>
    )
  }
  // instance
  return (
    <div className="heap-obj instance">
      <div className="heap-obj-header">
        <span className="heap-id">ID:{obj.id}</span>
        <span className="heap-label">instance of {obj.className}</span>
      </div>
      <div className="bindings instance-attrs">
        {obj.attrs.length === 0 && <div className="binding empty-binding">(no attrs)</div>}
        {obj.attrs.map((b, i) => (
          <div key={i} className={`binding${b.retired ? ' retired' : ''}`}>
            <span className="name">{b.name}</span>
            <span className="eq">=</span>
            <span className="value">{formatValueSimple(b.value)}</span>
          </div>
        ))}
      </div>
    </div>
  )
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
