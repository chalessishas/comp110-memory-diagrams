import type { ReactElement } from 'react'
import { useMemo, useState } from 'react'
import { CodeEditor } from './components/CodeEditor'
import { DiagramCanvas } from './components/DiagramCanvas'
import { StepControl } from './components/StepControl'
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

function App() {
  const embed = useMemo(() => isEmbed(), [])
  const [problemId, setProblemId] = useState(QZ00_PROBLEMS[0].id)
  const [source, setSource] = useState(QZ00_PROBLEMS[0].source)
  const [result, setResult] = useState<RunResult>({ kind: 'idle' })
  const [step, setStep] = useState(0)

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
  const currentProblem = QZ00_PROBLEMS.find((p) => p.id === problemId)

  return (
    <div className={`app${embed ? ' embed' : ''}`}>
      {!embed && (
        <header className="site-header">
          <div className="brand">
            <span className="brand-name">COMP110 Memory Diagrams</span>
            <span className="brand-tag">Interactive memory diagrams — v0 ruleset</span>
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
                  // Render problems grouped by `group`, preserving array order.
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
          <StepControl
            total={total}
            current={step}
            onChange={setStep}
            disabled={result.kind !== 'ok'}
          />
        </section>
      </main>

      {!embed && (
        <footer className="site-footer">
          <span>
            Built for <a href="https://comp110-26s.github.io/" target="_blank" rel="noreferrer">UNC COMP110</a>.
            Implements the v0 memory diagram rules. <a href="https://github.com/" target="_blank" rel="noreferrer">Source</a>.
          </span>
        </footer>
      )}
    </div>
  )
}

export default App
