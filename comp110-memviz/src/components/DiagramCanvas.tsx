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

  return (
    <div className="diagram">
      <section className="col stack">
        <header className="col-title">Function Call Stack</header>
        <div className="frames">
          {/* Active frame at the top. Globals is always at the bottom. */}
          {[...snapshot.stack].reverse().map((frame, idx) => (
            <FrameView key={idx} frame={frame} heap={snapshot.heap} isActive={idx === 0 && snapshot.stack.length > 1} />
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
  return (
    <div className={`frame${isActive ? ' active' : ''}${frame.name === 'Globals' ? ' globals' : ''}`}>
      <div className="frame-header">
        <span className="frame-name">{frame.name}</span>
        {frame.returnAddress !== null && <span className="ra">RA: {frame.returnAddress}</span>}
        {frame.returnValue !== null && (
          <span className="rv">RV: {formatValue(frame.returnValue, heap)}</span>
        )}
      </div>
      <div className="bindings">
        {Object.entries(frame.bindings).length === 0 && (
          <div className="binding empty-binding">(empty)</div>
        )}
        {Object.entries(frame.bindings).map(([name, value]) => (
          <div key={name} className="binding">
            <span className="name">{name}</span>
            <span className="eq">=</span>
            <span className="value">{formatValue(value, heap)}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function HeapObjectView({ obj }: { obj: HeapObject }) {
  return (
    <div className="heap-obj">
      <span className="heap-id">ID:{obj.id}</span>
      <span className="heap-label">Fn Lines {obj.lineStart}–{obj.lineEnd}</span>
      <span className="heap-name">({obj.name})</span>
    </div>
  )
}

function formatValue(v: Value, heap: HeapObject[]): string {
  switch (v.kind) {
    case 'int': return String(v.v)
    case 'float': return Number.isInteger(v.v) ? `${v.v}.0` : String(v.v)
    case 'str': return JSON.stringify(v.v)
    case 'none': return 'None'
    case 'ref': {
      const h = heap.find((x) => x.id === v.id)
      return h ? `→ ID:${v.id}` : `→ ID:${v.id} (missing)`
    }
  }
}
