import type { ReactElement } from 'react'
import { useMemo, useState } from 'react'
import { CanvasView } from './components/CanvasView'
import { CDiagramCanvas } from './components/CDiagramCanvas'
import { CodeEditor } from './components/CodeEditor'
import { DiagramCanvas } from './components/DiagramCanvas'
import { FeedbackButton } from './components/FeedbackButton'
import { StepControl } from './components/StepControl'
import { Timeline } from './components/Timeline'
import { QuizPractice } from './components/quiz/QuizPractice'
import { C_PROBLEMS } from './data/cProblems'
import { QZ00_PROBLEMS } from './data/qz00Problems'
import { run } from './interpreter/evaluator'
import { runC } from './interpreter/c/evaluator'
import type { CSnapshot } from './interpreter/c/types'
import type { Snapshot } from './interpreter/types'
import './App.css'

// One result type per language so the renderer can branch by snapshot
// shape. Python's heap is rich (functions, classes, lists, dicts,
// instances); C's heap is byte-addressed cells. They render with
// different components.
type RunResult =
  | { kind: 'idle' }
  | { kind: 'ok'; language: 'python'; snapshots: Snapshot[] }
  | { kind: 'ok'; language: 'c'; snapshots: CSnapshot[] }
  | { kind: 'error'; message: string }

type Language = 'python' | 'c'
type AppMode = 'tool' | 'quiz'

function isEmbed(): boolean {
  if (typeof window === 'undefined') return false
  const params = new URLSearchParams(window.location.search)
  return params.get('embed') === '1'
}

// Default auto-play cadence, tuned during mockup review. Students found
// 700ms felt "patient" — fast enough to keep flow, slow enough to read the
// narration. Slider lets them override.
const DEFAULT_AUTO_SPEED_MS = 700

type ViewMode = 'list' | 'canvas'

function App() {
  const embed = useMemo(() => isEmbed(), [])
  // Mode picks between the original memory-diagram tool and the new
  // knowledge-organized Quiz Practice. Embedded usage forces 'tool' so
  // existing course-site embeds keep working.
  const [mode, setMode] = useState<AppMode>('tool')
  const [language, setLanguage] = useState<Language>('python')
  // Each language keeps its own problem id + source so toggling Language
  // doesn't clobber edits in the other one.
  const [problemId, setProblemId] = useState(QZ00_PROBLEMS[0].id)
  const [source, setSource] = useState(QZ00_PROBLEMS[0].source)
  const [problemIdC, setProblemIdC] = useState(C_PROBLEMS[0].id)
  const [sourceC, setSourceC] = useState(C_PROBLEMS[0].source)
  const [result, setResult] = useState<RunResult>({ kind: 'idle' })
  const [step, setStep] = useState(0)
  const [autoSpeedMs, setAutoSpeedMs] = useState(DEFAULT_AUTO_SPEED_MS)
  // Default = list (the v0-faithful rendering students need for quizzes).
  // Canvas mode is the explorer view: drag, fold, see arrows.
  const [viewMode, setViewMode] = useState<ViewMode>('list')

  const onRun = () => {
    setStep(0)
    try {
      if (language === 'python') {
        const snapshots = run(source)
        setResult({ kind: 'ok', language: 'python', snapshots })
      } else {
        const snapshots = runC(sourceC)
        setResult({ kind: 'ok', language: 'c', snapshots })
      }
    } catch (e) {
      setResult({ kind: 'error', message: (e as Error).message })
    }
  }

  const onSelectProblem = (id: string) => {
    if (language === 'python') {
      const p = QZ00_PROBLEMS.find((x) => x.id === id)
      if (!p) return
      setProblemId(id)
      setSource(p.source)
    } else {
      const p = C_PROBLEMS.find((x) => x.id === id)
      if (!p) return
      setProblemIdC(id)
      setSourceC(p.source)
    }
    setResult({ kind: 'idle' })
    setStep(0)
  }

  const onSelectLanguage = (lang: Language) => {
    setLanguage(lang)
    setResult({ kind: 'idle' })
    setStep(0)
  }

  const snapshot = result.kind === 'ok' ? result.snapshots[step] ?? null : null
  const total = result.kind === 'ok' ? result.snapshots.length : 0
  const snapshots = result.kind === 'ok' ? result.snapshots : []
  // Per-language narrowed snapshot — Python and C snapshots are different
  // shapes (Python heap is rich, C heap is byte-cells) so each renderer
  // gets a typed `null`-or-self instead of the raw discriminated union.
  const pySnapshot: Snapshot | null =
    result.kind === 'ok' && result.language === 'python' ? result.snapshots[step] ?? null : null
  const cSnapshot: CSnapshot | null =
    result.kind === 'ok' && result.language === 'c' ? result.snapshots[step] ?? null : null
  const currentProblem = language === 'python'
    ? QZ00_PROBLEMS.find((p) => p.id === problemId)
    : C_PROBLEMS.find((p) => p.id === problemIdC)
  const currentSource = language === 'python' ? source : sourceC
  const currentSetSource = language === 'python' ? setSource : setSourceC
  const currentProblemId = language === 'python' ? problemId : problemIdC
  const currentProblemList = language === 'python' ? QZ00_PROBLEMS : C_PROBLEMS

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
              {mode === 'tool'
                ? 'v0 ruleset · Python + C — colored step timeline, auto speed, stronger step labels'
                : 'Quiz Practice — knowledge-organized concept drills with self-grading'}
            </span>
          </div>
          <div className="mode-toggle" role="tablist" aria-label="App mode">
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'tool'}
              className={mode === 'tool' ? 'mode-tab active' : 'mode-tab'}
              onClick={() => setMode('tool')}
            >
              Memory Diagram Tool
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={mode === 'quiz'}
              className={mode === 'quiz' ? 'mode-tab active' : 'mode-tab'}
              onClick={() => setMode('quiz')}
            >
              Quiz Practice
            </button>
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

      {mode === 'quiz' && !embed ? (
        <QuizPractice />
      ) : (
      <main className="workspace">
        <section className="left">
          <div className="view-toggle lang-toggle" role="tablist" aria-label="Language">
            <button
              type="button"
              role="tab"
              aria-selected={language === 'python'}
              className={language === 'python' ? 'view-tab active' : 'view-tab'}
              onClick={() => onSelectLanguage('python')}
              title="Python — full v0 ruleset (lists, dicts, classes, references)"
            >
              Python
            </button>
            <button
              type="button"
              role="tab"
              aria-selected={language === 'c'}
              className={language === 'c' ? 'view-tab active' : 'view-tab'}
              onClick={() => onSelectLanguage('c')}
              title="C — int/char/printf/control flow/functions (pointers + malloc coming next)"
            >
              C
            </button>
          </div>
          <div className="problem-bar">
            <label>
              Problem:{' '}
              <select value={currentProblemId} onChange={(e) => onSelectProblem(e.target.value)}>
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
                  for (const p of currentProblemList) {
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
            <CodeEditor value={currentSource} onChange={currentSetSource} highlightedLine={snapshot?.currentLine} />
          </div>
        </section>

        <section className="right">
          {/* Canvas/List toggle is Python-only — C's MVP renders one
              diagram style (no ref arrows yet, since pointers/malloc
              aren't implemented). When pointers land we'll re-enable
              Canvas mode for C too. */}
          {language === 'python' && (
            <div className="view-toggle" role="tablist" aria-label="Diagram view mode">
              <button
                type="button"
                role="tab"
                aria-selected={viewMode === 'list'}
                className={viewMode === 'list' ? 'view-tab active' : 'view-tab'}
                onClick={() => setViewMode('list')}
                title="COMP110 v0 list rendering — matches the quiz answer format"
              >
                List
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={viewMode === 'canvas'}
                className={viewMode === 'canvas' ? 'view-tab active' : 'view-tab'}
                onClick={() => setViewMode('canvas')}
                title="Free-form canvas — drag nodes, fold sections, follow ref arrows"
              >
                Canvas
              </button>
            </div>
          )}
          {language === 'python' ? (
            viewMode === 'list' ? (
              <DiagramCanvas snapshot={pySnapshot} />
            ) : (
              <CanvasView snapshot={pySnapshot} />
            )
          ) : (
            <CDiagramCanvas snapshot={cSnapshot} />
          )}
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
      )}

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
