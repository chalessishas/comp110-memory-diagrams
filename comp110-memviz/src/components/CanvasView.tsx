import { useEffect, useMemo, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  Handle,
  Position,
  useNodesState,
  useEdgesState,
  MarkerType,
} from '@xyflow/react'
import type { Node, Edge, NodeProps } from '@xyflow/react'
import dagre from 'dagre'
import '@xyflow/react/dist/style.css'
import type { Frame, HeapObject, Snapshot, Value } from '../interpreter/types'
import './CanvasView.css'

type Props = {
  snapshot: Snapshot | null
}

// ──────────────────────────────────────────────────────────────────────
// Helpers (intentional duplication w/ DiagramCanvas — keeping the two
// views fully independent so the list view's evolution doesn't ripple
// into the canvas and vice versa).

function groupByName<T extends { name: string; retired: boolean }>(arr: T[]) {
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
    .filter((g) => g.items.some((b) => !b.retired))
}

function groupByIndex<T extends { index: number; retired: boolean }>(arr: T[]) {
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

function fmt(v: Value): string {
  switch (v.kind) {
    case 'int': return String(v.v)
    case 'float': return Number.isInteger(v.v) ? `${v.v}.0` : String(v.v)
    case 'str': return JSON.stringify(v.v)
    case 'bool': return v.v ? 'True' : 'False'
    case 'none': return 'None'
    case 'ref': return `→ID:${v.id}`
  }
}

function dictKeyDisplay(tagged: string): string {
  const tag = tagged[0]
  const rest = tagged.slice(2)
  if (tag === 'S') return `'${rest}'`
  if (tag === 'I' || tag === 'F') return rest
  if (tag === 'B') return rest === '1' ? 'True' : 'False'
  if (tag === 'N') return 'None'
  if (tag === 'R') return `→ID:${rest}`
  return tagged
}

// ──────────────────────────────────────────────────────────────────────
// Custom node types

type FrameNodeData = {
  frame: Frame
  isActive: boolean
  collapsed: boolean
  onToggle: () => void
  // Indexes (in groupByName order) of bindings whose latest value is a ref —
  // these positions get a source Handle so the edge anchors to the row.
  refRowIdxs: Set<number>
}

type HeapNodeData = {
  obj: HeapObject
  collapsed: boolean
  onToggle: () => void
  refRowIdxs: Set<number>
}

function FrameNode({ data }: NodeProps<Node<FrameNodeData>>) {
  const { frame, isActive, collapsed, onToggle, refRowIdxs } = data
  const groups = groupByName(frame.bindings)
  const cls = [
    'cv-node',
    'cv-frame',
    isActive ? 'is-active' : '',
    frame.name === 'Globals' ? 'is-globals' : '',
    frame.retired ? 'is-retired' : '',
  ].filter(Boolean).join(' ')
  return (
    <div className={cls}>
      <div className="cv-header" onClick={onToggle}>
        <span className="cv-chevron">{collapsed ? '▸' : '▾'}</span>
        <span className="cv-title">{frame.name}</span>
        {frame.retired && <span className="cv-badge">returned</span>}
      </div>
      {!collapsed && (
        <div className="cv-body">
          {(frame.returnAddress !== null || frame.returnValue !== null) && (
            <div className="cv-rarv">
              {frame.returnAddress !== null && <div className="cv-row cv-meta">RA: {frame.returnAddress}</div>}
              {frame.returnValue !== null && <div className="cv-row cv-meta">RV: {fmt(frame.returnValue)}</div>}
            </div>
          )}
          {groups.length === 0 && <div className="cv-row cv-empty">(empty)</div>}
          {groups.map((g, gi) => (
            <div key={gi} className="cv-row cv-binding">
              <span className="cv-name">{g.name}</span>
              <span className="cv-eq">=</span>
              <span className="cv-value">
                {g.items.map((b, bi) => (
                  <span key={bi} className={b.retired ? 'cv-chunk retired' : 'cv-chunk active'}>
                    {fmt(b.value)}{bi < g.items.length - 1 ? ' ' : ''}
                  </span>
                ))}
              </span>
              {refRowIdxs.has(gi) && (
                <Handle
                  type="source"
                  position={Position.Right}
                  id={`b-${gi}`}
                  className="cv-handle"
                />
              )}
            </div>
          ))}
        </div>
      )}
      {/* Always render the target handle so collapsed nodes still receive arrows */}
      <Handle type="target" position={Position.Left} id="t" className="cv-handle cv-handle-target" />
    </div>
  )
}

function HeapNode({ data }: NodeProps<Node<HeapNodeData>>) {
  const { obj, collapsed, onToggle, refRowIdxs } = data
  let body: React.ReactNode = null
  let label = ''
  let kindCls = ''
  if (obj.kind === 'function') {
    label = `fn ${obj.lineStart}–${obj.lineEnd}`
    kindCls = 'kind-fn'
    body = <div className="cv-row cv-meta">{obj.name}</div>
  } else if (obj.kind === 'class') {
    label = `class ${obj.lineStart}–${obj.lineEnd}`
    kindCls = 'kind-class'
    body = <div className="cv-row cv-meta">{obj.name}</div>
  } else if (obj.kind === 'list') {
    const groups = groupByIndex(obj.slots)
    label = 'list'
    kindCls = 'kind-list'
    body = (
      <>
        {groups.length === 0 && <div className="cv-row cv-empty">(empty)</div>}
        {groups.map((g, gi) => (
          <div key={gi} className="cv-row cv-binding">
            <span className="cv-name">[{g.index}]</span>
            <span className="cv-eq">=</span>
            <span className="cv-value">
              {g.items.map((s, si) => (
                <span key={si} className={s.retired ? 'cv-chunk retired' : 'cv-chunk active'}>
                  {fmt(s.value)}{si < g.items.length - 1 ? ' ' : ''}
                </span>
              ))}
            </span>
            {refRowIdxs.has(gi) && (
              <Handle type="source" position={Position.Right} id={`s-${gi}`} className="cv-handle" />
            )}
          </div>
        ))}
      </>
    )
  } else if (obj.kind === 'dict') {
    const groups = groupByName(obj.entries)
    label = 'dict'
    kindCls = 'kind-dict'
    body = (
      <>
        {groups.length === 0 && <div className="cv-row cv-empty">(empty)</div>}
        {groups.map((g, gi) => (
          <div key={gi} className="cv-row cv-binding">
            <span className="cv-name">{dictKeyDisplay(g.name)}</span>
            <span className="cv-eq">:</span>
            <span className="cv-value">
              {g.items.map((e, ei) => (
                <span key={ei} className={e.retired ? 'cv-chunk retired' : 'cv-chunk active'}>
                  {fmt(e.value)}{ei < g.items.length - 1 ? ' ' : ''}
                </span>
              ))}
            </span>
            {refRowIdxs.has(gi) && (
              <Handle type="source" position={Position.Right} id={`e-${gi}`} className="cv-handle" />
            )}
          </div>
        ))}
      </>
    )
  } else {
    const groups = groupByName(obj.attrs)
    label = obj.className
    kindCls = 'kind-instance'
    body = (
      <>
        {groups.length === 0 && <div className="cv-row cv-empty">(no attrs)</div>}
        {groups.map((g, gi) => (
          <div key={gi} className="cv-row cv-binding">
            <span className="cv-name">{g.name}</span>
            <span className="cv-eq">=</span>
            <span className="cv-value">
              {g.items.map((a, ai) => (
                <span key={ai} className={a.retired ? 'cv-chunk retired' : 'cv-chunk active'}>
                  {fmt(a.value)}{ai < g.items.length - 1 ? ' ' : ''}
                </span>
              ))}
            </span>
            {refRowIdxs.has(gi) && (
              <Handle type="source" position={Position.Right} id={`a-${gi}`} className="cv-handle" />
            )}
          </div>
        ))}
      </>
    )
  }
  return (
    <div className={`cv-node cv-heap ${kindCls}`}>
      <div className="cv-header" onClick={onToggle}>
        <span className="cv-chevron">{collapsed ? '▸' : '▾'}</span>
        <span className="cv-id">ID:{obj.id}</span>
        <span className="cv-label">{label}</span>
      </div>
      {!collapsed && <div className="cv-body">{body}</div>}
      <Handle type="target" position={Position.Left} id="t" className="cv-handle cv-handle-target" />
    </div>
  )
}

const nodeTypes = { frame: FrameNode, heap: HeapNode }

// ──────────────────────────────────────────────────────────────────────
// Snapshot → React Flow nodes + edges

const ROW_H = 22
const HEADER_H = 32
const NODE_W = 220
const NODE_PAD = 14

function estimateFrameSize(frame: Frame, collapsed: boolean) {
  if (collapsed) return { width: NODE_W, height: HEADER_H }
  const groups = groupByName(frame.bindings)
  const rarvRows = (frame.returnAddress !== null ? 1 : 0) + (frame.returnValue !== null ? 1 : 0)
  const rows = Math.max(1, groups.length) + rarvRows
  return { width: NODE_W, height: HEADER_H + rows * ROW_H + NODE_PAD }
}

function estimateHeapSize(obj: HeapObject, collapsed: boolean) {
  if (collapsed) return { width: NODE_W, height: HEADER_H }
  let rows = 1
  if (obj.kind === 'instance') rows = Math.max(1, groupByName(obj.attrs).length)
  else if (obj.kind === 'list') rows = Math.max(1, groupByIndex(obj.slots).length)
  else if (obj.kind === 'dict') rows = Math.max(1, groupByName(obj.entries).length)
  return { width: NODE_W, height: HEADER_H + rows * ROW_H + NODE_PAD }
}

function activeRefRowIdxs(items: { name?: string; index?: number; value: Value; retired: boolean }[],
                          group: 'name' | 'index'): Set<number> {
  const groups = group === 'name'
    ? groupByName(items as { name: string; value: Value; retired: boolean }[])
    : groupByIndex(items as { index: number; value: Value; retired: boolean }[])
  const refIdxs = new Set<number>()
  groups.forEach((g, gi) => {
    const latest = g.items[g.items.length - 1]
    if (latest && !latest.retired && latest.value.kind === 'ref') refIdxs.add(gi)
  })
  return refIdxs
}

function build(snapshot: Snapshot, collapsed: Record<string, boolean>, toggle: (id: string) => void) {
  const nodes: Node[] = []
  const edges: Edge[] = []

  // Active frame index (deepest non-retired)
  let activeIdx = -1
  for (let i = snapshot.stack.length - 1; i >= 0; i--) {
    if (!snapshot.stack[i].retired) { activeIdx = i; break }
  }

  snapshot.stack.forEach((frame, fi) => {
    const id = `frame-${fi}`
    const isCol = !!collapsed[id]
    const refRowIdxs = activeRefRowIdxs(frame.bindings as never, 'name')
    const size = estimateFrameSize(frame, isCol)
    nodes.push({
      id,
      type: 'frame',
      position: { x: 0, y: 0 },
      data: {
        frame,
        isActive: fi === activeIdx,
        collapsed: isCol,
        onToggle: () => toggle(id),
        refRowIdxs,
      } satisfies FrameNodeData,
      width: size.width,
      height: size.height,
    })
    // Frame → heap edges (one per ref-valued binding)
    const groups = groupByName(frame.bindings)
    groups.forEach((g, gi) => {
      const latest = g.items[g.items.length - 1]
      if (latest && !latest.retired && latest.value.kind === 'ref') {
        edges.push({
          id: `e-${id}-b${gi}-${latest.value.id}`,
          source: id,
          sourceHandle: `b-${gi}`,
          target: `heap-${latest.value.id}`,
          targetHandle: 't',
          type: 'smoothstep',
          markerEnd: { type: MarkerType.ArrowClosed, color: '#1e7084' },
          style: { stroke: '#1e7084', strokeWidth: 1.5 },
        })
      }
    })
  })

  snapshot.heap.forEach((obj) => {
    const id = `heap-${obj.id}`
    const isCol = !!collapsed[id]
    let refRowIdxs = new Set<number>()
    if (obj.kind === 'instance') refRowIdxs = activeRefRowIdxs(obj.attrs as never, 'name')
    else if (obj.kind === 'list') refRowIdxs = activeRefRowIdxs(obj.slots as never, 'index')
    else if (obj.kind === 'dict') refRowIdxs = activeRefRowIdxs(obj.entries as never, 'name')
    const size = estimateHeapSize(obj, isCol)
    nodes.push({
      id,
      type: 'heap',
      position: { x: 0, y: 0 },
      data: { obj, collapsed: isCol, onToggle: () => toggle(id), refRowIdxs } satisfies HeapNodeData,
      width: size.width,
      height: size.height,
    })
    // Heap → heap edges
    const items: { gi: number; value: Value }[] = []
    if (obj.kind === 'instance') {
      groupByName(obj.attrs).forEach((g, gi) => {
        const latest = g.items[g.items.length - 1]
        if (latest && !latest.retired) items.push({ gi, value: latest.value })
      })
      items.forEach(({ gi, value }) => {
        if (value.kind === 'ref') {
          edges.push(makeEdge(id, `a-${gi}`, value.id))
        }
      })
    } else if (obj.kind === 'list') {
      groupByIndex(obj.slots).forEach((g, gi) => {
        const latest = g.items[g.items.length - 1]
        if (latest && !latest.retired && latest.value.kind === 'ref') {
          edges.push(makeEdge(id, `s-${gi}`, latest.value.id))
        }
      })
    } else if (obj.kind === 'dict') {
      groupByName(obj.entries).forEach((g, gi) => {
        const latest = g.items[g.items.length - 1]
        if (latest && !latest.retired && latest.value.kind === 'ref') {
          edges.push(makeEdge(id, `e-${gi}`, latest.value.id))
        }
      })
    }
  })

  return { nodes, edges }
}

function makeEdge(sourceId: string, sourceHandle: string, heapId: number): Edge {
  return {
    id: `e-${sourceId}-${sourceHandle}-${heapId}`,
    source: sourceId,
    sourceHandle,
    target: `heap-${heapId}`,
    targetHandle: 't',
    type: 'smoothstep',
    markerEnd: { type: MarkerType.ArrowClosed, color: '#805ad5' },
    style: { stroke: '#805ad5', strokeWidth: 1.5 },
  }
}

function applyDagre(nodes: Node[], edges: Edge[]): Node[] {
  const g = new dagre.graphlib.Graph()
  g.setGraph({ rankdir: 'LR', nodesep: 28, ranksep: 80, marginx: 16, marginy: 16 })
  g.setDefaultEdgeLabel(() => ({}))
  nodes.forEach((n) => {
    g.setNode(n.id, { width: n.width ?? NODE_W, height: n.height ?? 60 })
  })
  edges.forEach((e) => g.setEdge(e.source, e.target))
  dagre.layout(g)
  return nodes.map((n) => {
    const pos = g.node(n.id)
    const w = n.width ?? NODE_W
    const h = n.height ?? 60
    return { ...n, position: { x: pos.x - w / 2, y: pos.y - h / 2 } }
  })
}

// ──────────────────────────────────────────────────────────────────────
// Component

export function CanvasView({ snapshot }: Props) {
  const [collapsed, setCollapsed] = useState<Record<string, boolean>>({})
  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([])
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([])

  const toggle = useMemo(
    () => (id: string) => setCollapsed((prev) => ({ ...prev, [id]: !prev[id] })),
    [],
  )

  // Rebuild + re-layout whenever the snapshot or collapse state changes.
  // User drags within a step are preserved by React Flow's internal state
  // until the next snapshot tick.
  useEffect(() => {
    if (!snapshot) {
      setNodes([])
      setEdges([])
      return
    }
    const built = build(snapshot, collapsed, toggle)
    const positioned = applyDagre(built.nodes, built.edges)
    setNodes(positioned)
    setEdges(built.edges)
  }, [snapshot, collapsed, toggle, setNodes, setEdges])

  if (!snapshot) {
    return (
      <div className="cv-placeholder">
        <p>Press <strong>Run</strong> to see the canvas. Drag nodes to rearrange. Click a header to fold.</p>
      </div>
    )
  }

  return (
    <div className="cv-wrap">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        nodeTypes={nodeTypes}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        fitView
        fitViewOptions={{ padding: 0.15 }}
        minZoom={0.3}
        maxZoom={2}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={20} size={1} color="#cbd5e0" />
        <Controls showInteractive={false} />
      </ReactFlow>
    </div>
  )
}
