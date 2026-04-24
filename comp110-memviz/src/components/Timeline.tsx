import type { Snapshot, SnapshotEvent } from '../interpreter/types'
import './Timeline.css'

type Props = {
  snapshots: Snapshot[]
  current: number
  onSelect: (step: number) => void
}

// Event → visible color + teaching label. Colors are lifted from the existing
// COMP110 palette (App.css): teal for declare, warn-amber for assign, blue
// for call, green for return, teal-dark for print; neutral gray for control
// (flow-only, no memory change) and meta (program start/end, errors).
const EVENT_COLOR: Record<SnapshotEvent, string> = {
  declare: '#1e7084', // teal
  assign: '#d69e2e', // warn amber (matches active-frame accent)
  call: '#2b6cb0', // blue
  return: '#2f855a', // green
  print: '#185968', // teal-dark
  control: '#a0aec0', // gray-400 — flow step, no memory change
  meta: '#4a5568', // gray-700 — program start/end, errors
}

const EVENT_LABEL: Record<SnapshotEvent, string> = {
  declare: 'declare',
  assign: 'assign',
  call: 'call',
  return: 'return',
  print: 'print',
  control: 'flow',
  meta: 'meta',
}

// A strip of one colored dot per step. Click any dot to jump to that step.
// The active step is enlarged and ringed. A legend beneath the strip shows
// the event vocabulary — students build intuition for "red-ish = assignment,
// blue = call" over a few problems, which makes dense programs skimmable.
export function Timeline({ snapshots, current, onSelect }: Props) {
  if (snapshots.length === 0) return null

  // Which events actually appear in this run — we only show legend chips
  // for colors the student will actually see on this strip.
  const seen = new Set<SnapshotEvent>()
  for (const s of snapshots) seen.add(s.event)

  return (
    <div className="timeline" role="group" aria-label="Step timeline">
      <div className="timeline-strip">
        {snapshots.map((s, i) => {
          const active = i === current
          return (
            <button
              key={i}
              type="button"
              className={`timeline-dot${active ? ' active' : ''}`}
              style={{ background: EVENT_COLOR[s.event] }}
              onClick={() => onSelect(i)}
              aria-label={`Step ${i + 1}: ${EVENT_LABEL[s.event]} — ${s.narration}`}
              aria-current={active ? 'step' : undefined}
              title={`Step ${i + 1} · ${EVENT_LABEL[s.event]} · line ${s.currentLine || '—'}`}
            />
          )
        })}
      </div>
      <div className="timeline-legend" aria-hidden="true">
        {(['declare', 'assign', 'call', 'return', 'print', 'control'] as const)
          .filter((e) => seen.has(e))
          .map((e) => (
            <span key={e} className="timeline-legend-item">
              <span
                className="timeline-legend-swatch"
                style={{ background: EVENT_COLOR[e] }}
              />
              {EVENT_LABEL[e]}
            </span>
          ))}
      </div>
    </div>
  )
}
