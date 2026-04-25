import type { ReactNode } from 'react'
import type {
  CBinding, CFrame, CHeapBlock, CSnapshot, CType, CValue,
} from '../interpreter/c/types'
import './DiagramCanvas.css'

type Props = {
  snapshot: CSnapshot | null
}

// C-side memory diagram. Mirrors DiagramCanvas's 3-column Stack | Heap |
// Output layout but renders C-specific bindings (typed) and heap blocks
// (malloc'd cells with synthetic addresses).
export function CDiagramCanvas({ snapshot }: Props) {
  if (!snapshot) {
    return (
      <div className="diagram placeholder">
        <p>Write some C code and press <strong>Run</strong> to see the diagram.</p>
      </div>
    )
  }

  let activeIdx = -1
  for (let i = snapshot.stack.length - 1; i >= 0; i--) {
    if (!snapshot.stack[i].retired) {
      activeIdx = i
      break
    }
  }

  return (
    <div className="diagram">
      <section className="col stack">
        <header className="col-title">Stack</header>
        <div className="frames">
          {snapshot.stack.map((frame, idx) => (
            <CFrameView key={idx} frame={frame} isActive={idx === activeIdx} />
          ))}
        </div>
      </section>

      <section className="col heap">
        <header className="col-title">Heap</header>
        <div className="heap-objects">
          {snapshot.heap.length === 0 && <p className="empty">(no heap blocks yet — malloc / arrays coming soon)</p>}
          {snapshot.heap.map((h) => (
            <CHeapBlockView key={h.id} block={h} />
          ))}
        </div>
      </section>

      <section className="col output">
        <header className="col-title">Output</header>
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

function CFrameView({ frame, isActive }: { frame: CFrame; isActive: boolean }) {
  const cls = [
    'frame',
    isActive ? 'active' : '',
    frame.name === 'Globals' ? 'globals' : '',
    frame.retired ? 'retired' : '',
  ]
    .filter(Boolean)
    .join(' ')
  const hasRARV = frame.returnAddress !== null || frame.returnValue !== null
  const bindingGroups = groupByName(frame.bindings)
  const bindingsBlock = (
    <div className="bindings">
      {bindingGroups.length === 0 && (
        <div className="binding empty-binding">(empty)</div>
      )}
      {bindingGroups.map((g, i) => (
        <div key={i} className="binding">
          <span className="name">{typeToStr(g.items[0].type)} {g.name}</span>
          <span className="eq">=</span>
          <span className="value">
            {renderHistory(g.items.map((b) => ({ retired: b.retired, text: valueToDisplay(b.value) })))}
          </span>
        </div>
      ))}
    </div>
  )
  return (
    <div className={cls}>
      <div className="frame-header">
        <span className="frame-name">{frame.name}</span>
      </div>
      {hasRARV ? (
        <div className="frame-body">
          <div className="ra-rv">
            {frame.returnAddress !== null && <div className="ra">RA: {frame.returnAddress}</div>}
            {frame.returnValue !== null && (
              <div className="rv">RV: {valueToDisplay(frame.returnValue)}</div>
            )}
          </div>
          {bindingsBlock}
        </div>
      ) : (
        bindingsBlock
      )}
    </div>
  )
}

function CHeapBlockView({ block }: { block: CHeapBlock }) {
  const cls = ['heap-obj', 'list', block.freed ? 'retired' : ''].filter(Boolean).join(' ')
  return (
    <div className={cls}>
      <div className="heap-obj-header">
        <span className="heap-id">0x{block.address.toString(16)}</span>
        <span className="heap-label">{typeToStr(block.elementType)}[{block.length}]{block.freed ? ' (freed)' : ''}</span>
      </div>
      <div className="bindings list-slots">
        {block.cells.map((cell, i) => (
          <div key={i} className="binding">
            <span className="name">[{cell.index}]</span>
            <span className="eq">=</span>
            <span className="value">
              <span className={cell.retired ? 'chunk retired' : 'chunk active'}>
                {valueToDisplay(cell.value)}
              </span>
            </span>
          </div>
        ))}
      </div>
    </div>
  )
}

function groupByName(arr: CBinding[]): { name: string; items: CBinding[] }[] {
  const firstIdx = new Map<string, number>()
  arr.forEach((b, i) => {
    if (!firstIdx.has(b.name)) firstIdx.set(b.name, i)
  })
  const groups = new Map<string, CBinding[]>()
  for (const b of arr) {
    const existing = groups.get(b.name)
    if (existing) existing.push(b)
    else groups.set(b.name, [b])
  }
  return [...firstIdx.entries()]
    .sort((a, b) => a[1] - b[1])
    .map(([name]) => ({ name, items: groups.get(name)! }))
    .filter((g) => g.items.some((b) => !b.retired))
}

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

function valueToDisplay(v: CValue): string {
  switch (v.kind) {
    case 'int': return String(v.v)
    case 'char': return `'${printableChar(v.v)}' (${v.v})`
    case 'ptr': return v.address === 0 ? 'NULL' : `0x${v.address.toString(16)}`
    case 'uninit': return '?'
  }
}

function printableChar(code: number): string {
  if (code === 10) return '\\n'
  if (code === 9) return '\\t'
  if (code === 0) return '\\0'
  if (code === 13) return '\\r'
  if (code >= 32 && code <= 126) return String.fromCharCode(code)
  return `\\x${code.toString(16).padStart(2, '0')}`
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
