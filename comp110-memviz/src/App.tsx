import type { ReactElement } from 'react'
import { useMemo, useState } from 'react'
import { CodeEditor } from './components/CodeEditor'
import { DiagramCanvas } from './components/DiagramCanvas'
import { FeedbackButton } from './components/FeedbackButton'
import { StepControl } from './components/StepControl'
import { Timeline } from './components/Timeline'
import { QZ00_PROBLEMS } from './data/qz00Problems'
import { run } from './interpreter/evaluator'
import type { Snapshot } from './interpreter/types'
import './App.css'

type RunResult =
  | { kind: 'idle' }
  | { kind: 'ok'; snapshots: Snapshot[] }
  | { kind: 'error'; message: string }

function isEmbed(): boolean {
  if (typeof window === 'undefined') return false
  const params = new URLSearchParams(window.location.search)
  return params.get('embed') === '1'
}

// Default auto-play cadence, tuned during mockup review. Students found
// 700ms felt "patient" — fast enough to keep flow, slow enough to read the
// narration. Slider lets them override.
const DEFAULT_AUTO_SPEED_MS = 700

function App() {
  const embed = useMemo(() => isEmbed(), [])
  const [problemId, setProblemId] = useState(QZ00_PROBLEMS[0].id)
  const [source, setSource] = useState(QZ00_PROBLEMS[0].source)
  const [result, setResult] = useState<RunResult>({ kind: 'idle' })
  const [step, setStep] = useState(0)
  const [autoSpeedMs, setAutoSpeedMs] = useState(DEFAULT_AUTO_SPEED_MS)

  const onRun = () => {
    setStep(0)
    try {
      const snapshots = run(source)
      setResult({ kind: 'ok', snapshots })
    } catch (e) {
      setResult({ kind: 'error', message: (e as Error).message })
    }
  }

  const onSelectProblem = (id: string) => {
    const p = QZ00_PROBLEMS.find((x) => x.id === id)
    if (!p) return
    setProblemId(id)
    setSource(p.source)
    setResult({ kind: 'idle' })
    setStep(0)
  }

  const snapshot = result.kind === 'ok' ? result.snapshots[step] ?? null : null
  const total = result.kind === 'ok' ? result.snapshots.length : 0
  const snapshots = result.kind === 'ok' ? result.snapshots : []
  const currentProblem = QZ00_PROBLEMS.find((p) => p.id === problemId)

  return (
    <div
      className={`app${embed ? ' embed' : ''}`}
      data-memviz-version="2"
    >
      {!embed && (
        <header className="site-header">
          <div className="brand">
            <span className="brand-name">COMP110 Memory Diagrams</span>
            <span className="brand-tag">
              v0 ruleset — V2: colored step timeline, auto speed, stronger step labels
            </span>
          </div>
          <nav className="site-nav">
            <a href="https://comp110-26s.github.io/" target="_blank" rel="noreferrer">Course site ↗</a>
            <a
              href="https://comp110-26s.github.io/static/slides/memory_diagrams_v0.pdf"
              target="_blank"
              rel="noreferrer"
            >
              Rules (PDF) ↗
            </a>
          </nav>
        </header>
      )}

      <main className="workspace">
        <section className="left">
          <div className="problem-bar">
            <label>
              Problem:{' '}
              <select value={problemId} onChange={(e) => onSelectProblem(e.target.value)}>
                {(() => {
                  const out: ReactElement[] = []
                  let currentGroup: string | undefined = undefined
                  let groupItems: ReactElement[] = []
                  const flush = () => {
                    if (groupItems.length === 0) return
                    if (currentGroup) {
                      out.push(
                        <optgroup key={`g-${currentGroup}-${out.length}`} label={currentGroup}>
                          {groupItems}
                        </optgroup>,
                      )
                    } else {
                      out.push(...groupItems)
                    }
                    groupItems = []
                  }
                  for (const p of QZ00_PROBLEMS) {
                    if (p.group !== currentGroup) {
                      flush()
                      currentGroup = p.group
                    }
                    groupItems.push(
                      <option key={p.id} value={p.id}>
                        {p.title}
                      </option>,
                    )
                  }
                  flush()
                  return out
                })()}
              </select>
            </label>
            <button type="button" className="run-btn" onClick={onRun}>▶ Run</button>
          </div>
          {currentProblem && !embed && (
            <p className="prompt">{currentProblem.prompt}</p>
          )}
          <div className="editor-wrap">
            <CodeEditor value={source} onChange={setSource} highlightedLine={snapshot?.currentLine} />
          </div>
        </section>

        <section className="right">
          <DiagramCanvas snapshot={snapshot} />
          {result.kind === 'ok' && snapshot && (
            <div className="narration">
              <span className="step-label">Step {step + 1} / {total}:</span>{' '}
              {snapshot.currentLine > 0 && <span className="line-ref">line {snapshot.currentLine} —</span>}{' '}
              {snapshot.narration}
            </div>
          )}
          {result.kind === 'ok' && snapshot?.error && (
            <div className="error-banner">
              <strong>Error:</strong> {snapshot.error}
            </div>
          )}
          {result.kind === 'error' && (
            <div className="error-banner">
              <strong>Parse error:</strong> {result.message}
            </div>
          )}
          {/* Timeline strip: one colored dot per step, clickable to jump.
              Dots are colored by the snapshot.event field inferred in
              evaluator.ts. Only renders once a run has produced snapshots. */}
          {result.kind === 'ok' && snapshots.length > 0 && (
            <Timeline snapshots={snapshots} current={step} onSelect={setStep} />
          )}
          <div className="step-row">
            <StepControl
              total={total}
              current={step}
              onChange={setStep}
              disabled={result.kind !== 'ok'}
              autoSpeedMs={autoSpeedMs}
              showProgress
            />
            {/* Speed slider sits beside the step controls. Range tuned to
                "slow enough to read long narrations" → "fast enough to
                skim through a well-understood problem". */}
            <label className="speed-control" title="Auto-play speed">
              <span className="speed-label">Speed</span>
              <input
                type="range"
                min={200}
                max={2000}
                step={100}
                value={autoSpeedMs}
                onChange={(e) => setAutoSpeedMs(Number(e.target.value))}
                aria-label="Auto-play speed in milliseconds per step"
              />
              <span className="speed-value">{autoSpeedMs}ms</span>
            </label>
          </div>
        </section>
      </main>

      {!embed && (
        <footer className="site-footer">
          <span>
            Built for <a href="https://comp110-26s.github.io/" target="_blank" rel="noreferrer">UNC COMP110</a>.
            Implements the v0 memory diagram rules. <a href="https://github.com/chalessishas/comp110-memory-diagrams" target="_blank" rel="noreferrer">Source</a>.
          </span>
        </footer>
      )}

      <FeedbackButton hidden={embed} />
    </div>
  )
}

export default App
