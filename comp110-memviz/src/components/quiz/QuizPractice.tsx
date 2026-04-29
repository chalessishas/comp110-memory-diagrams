import { useMemo, useState } from 'react'
import CodeMirror from '@uiw/react-codemirror'
import { python } from '@codemirror/lang-python'
import { DiagramCanvas } from '../DiagramCanvas'
import { StepControl } from '../StepControl'
import { Timeline } from '../Timeline'
import { run } from '../../interpreter/evaluator'
import type { Snapshot } from '../../interpreter/types'
import { QUIZ_BANK } from '../../data/quiz/quizBank'
import type {
  EvaluateQuestion,
  IdentifyLinesQuestion,
  MCQQuestion,
  MemoryDiagramQuestion,
  Question,
  Topic,
  WriteCodeQuestion,
  WriteCodeValidator,
} from './types'
import { TOPIC_META } from './types'
import './QuizPractice.css'

// --- Topic ordering for sidebar (concept progression, not quiz order) ---
const TOPIC_ORDER: Topic[] = [
  'types-expressions',
  'functions-anatomy',
  'function-writing',
  'conditionals-boolean',
  'recursion',
  'looping',
  'collections',
  'function-writing-full',
  'classes',
  'class-writing',
  'linked-lists',
  'memory-diagrams',
]

// --- Helpers ------------------------------------------------------------

// Snake_case "QZ00 Q1.1" → display "1.1" — strips the QZ prefix so the
// quiz feels like a self-contained drill, not a reprint.
function shortLabel(source: string | undefined, fallbackIdx: number): string {
  if (!source) return `${fallbackIdx + 1}`
  const m = /Q(\d+)(?:\.(\d+))?/.exec(source)
  if (!m) return source
  return m[2] ? `${m[1]}.${m[2]}` : `${m[1]}`
}

// Render code with 1-indexed line numbers, gutter style. Used by the
// question-card preview.
function CodeBlock({ code, highlightLines }: { code: string; highlightLines?: Set<number> }) {
  const lines = code.split('\n')
  return (
    <pre className="code-block">
      {lines.map((line, i) => {
        const lineNum = i + 1
        const isHl = highlightLines?.has(lineNum)
        return (
          <div key={i} className={`code-line${isHl ? ' code-line-hl' : ''}`}>
            <span className="code-gutter">{lineNum}</span>
            <span className="code-content">{line || ' '}</span>
          </div>
        )
      })}
    </pre>
  )
}

// --- MCQ ----------------------------------------------------------------

function MCQAnswer({
  q,
  selected,
  submitted,
  onChange,
}: {
  q: MCQQuestion
  selected: number | null
  submitted: boolean
  onChange: (n: number) => void
}) {
  return (
    <div className="mcq">
      {q.choices.map((c, i) => {
        const isSelected = selected === i
        const isCorrect = i === q.answer
        const stateClass = !submitted
          ? isSelected
            ? 'mcq-row mcq-row-selected'
            : 'mcq-row'
          : isCorrect
          ? 'mcq-row mcq-row-correct'
          : isSelected
          ? 'mcq-row mcq-row-wrong'
          : 'mcq-row mcq-row-faded'
        return (
          <button
            type="button"
            key={i}
            className={stateClass}
            disabled={submitted}
            onClick={() => onChange(i)}
          >
            <span className={`mcq-bubble${isSelected ? ' filled' : ''}`} aria-hidden="true" />
            <span className="mcq-label">{c.label}</span>
          </button>
        )
      })}
    </div>
  )
}

function gradeMCQ(q: MCQQuestion, selected: number | null) {
  if (selected === null) return { score: 0, max: 1, correct: false, hint: 'No answer selected.' }
  return {
    score: selected === q.answer ? 1 : 0,
    max: 1,
    correct: selected === q.answer,
    hint: selected === q.answer ? 'Correct.' : `Correct answer: ${q.choices[q.answer].label}`,
  }
}

// --- Evaluate -----------------------------------------------------------

type EvaluateState = { value: string; type: string }

function EvaluateAnswer({
  q,
  state,
  submitted,
  onChange,
}: {
  q: EvaluateQuestion
  state: EvaluateState
  submitted: boolean
  onChange: (s: EvaluateState) => void
}) {
  return (
    <div className="evaluate">
      <label className="evaluate-field">
        <span className="evaluate-label">Value</span>
        <input
          type="text"
          className="evaluate-input"
          value={state.value}
          disabled={submitted}
          placeholder={q.isError ? 'e.g., Error' : 'e.g., 14.1'}
          onChange={(e) => onChange({ ...state, value: e.target.value })}
        />
      </label>
      {!q.isError && (
        <label className="evaluate-field">
          <span className="evaluate-label">Type</span>
          <input
            type="text"
            className="evaluate-input evaluate-type"
            value={state.type}
            disabled={submitted}
            placeholder="e.g., float"
            onChange={(e) => onChange({ ...state, type: e.target.value })}
          />
        </label>
      )}
    </div>
  )
}

function gradeEvaluate(q: EvaluateQuestion, state: EvaluateState) {
  const v = state.value.trim()
  const t = state.type.trim()
  const partial: string[] = []

  // Value
  let valueScore = 0
  const exactValueMatch = q.acceptedValues.some((a) => a.trim() === v)
  if (exactValueMatch) {
    valueScore = 0.5
    if (v !== q.preferredValue) {
      const rule = q.partialCreditRules?.[0]
      if (rule) {
        valueScore -= rule.deduction
        partial.push(`Value form: ${rule.description} (-${rule.deduction})`)
      }
    }
  }

  // Type (or skipped if isError)
  let typeScore = 0
  if (q.isError) {
    typeScore = 0.5
  } else if (q.acceptedTypes.some((a) => a.trim().toLowerCase() === t.toLowerCase())) {
    typeScore = 0.5
  }

  const score = Math.max(0, Math.min(1, valueScore + typeScore))
  const correct = score === 1
  const hint = correct
    ? 'Correct.'
    : `Expected value: ${q.preferredValue}` + (q.isError ? '' : ` · Type: ${q.preferredType}`)
  return { score, max: 1, correct, hint, partial }
}

// --- Identify Lines -----------------------------------------------------

function IdentifyLinesAnswer({
  q,
  selected,
  submitted,
  onToggle,
}: {
  q: IdentifyLinesQuestion
  selected: Set<number>
  submitted: boolean
  onToggle: (n: number) => void
}) {
  const correctSet = new Set(q.answer)
  return (
    <div className="identify">
      <CodeBlock code={q.code ?? ''} highlightLines={submitted ? correctSet : undefined} />
      <div className="identify-options">
        {q.lineOptions.map((line) => {
          const isSelected = selected.has(line)
          const isCorrect = correctSet.has(line)
          let cls = 'line-bubble'
          if (submitted) {
            if (isCorrect && isSelected) cls += ' line-bubble-correct'
            else if (isCorrect) cls += ' line-bubble-missed'
            else if (isSelected) cls += ' line-bubble-wrong'
          } else if (isSelected) cls += ' line-bubble-selected'
          return (
            <button
              type="button"
              key={line}
              className={cls}
              disabled={submitted}
              onClick={() => onToggle(line)}
            >
              {line}
            </button>
          )
        })}
      </div>
    </div>
  )
}

function gradeIdentifyLines(q: IdentifyLinesQuestion, selected: Set<number>) {
  const allValidAnswers = [q.answer, ...(q.alternateAnswers ?? [])]
  // Try each accepted answer set and take the best score.
  let best = { score: 0, partial: [] as string[] }
  for (const target of allValidAnswers) {
    const targetSet = new Set(target)
    if (q.scoring === 'all-or-nothing') {
      const exact = targetSet.size === selected.size && [...targetSet].every((n) => selected.has(n))
      if (exact) best = { score: 1, partial: [] }
    } else {
      const correct = [...selected].filter((n) => targetSet.has(n)).length
      const wrong = [...selected].filter((n) => !targetSet.has(n)).length
      const missed = [...targetSet].filter((n) => !selected.has(n)).length
      // 0.3 per correct line, capped at 1, less penalty for wrongs.
      const partialScore = Math.max(0, Math.min(1, correct * 0.3 - wrong * 0.15))
      if (partialScore > best.score) {
        best = {
          score: partialScore,
          partial:
            wrong > 0 || missed > 0
              ? [`${correct} of ${target.length} correct, ${wrong} wrong selection${wrong === 1 ? '' : 's'}, ${missed} missed`]
              : [],
        }
      }
    }
  }
  const correct = best.score === 1
  const hint = correct ? 'Correct.' : `Correct lines: ${q.answer.join(', ')}`
  return { ...best, max: 1, correct, hint }
}

// --- Write Code ---------------------------------------------------------

function WriteCodeAnswer({
  source,
  submitted,
  onChange,
}: {
  source: string
  submitted: boolean
  onChange: (s: string) => void
}) {
  return (
    <div className="write-code">
      <CodeMirror
        value={source}
        height="160px"
        extensions={[python()]}
        onChange={(v) => onChange(v)}
        readOnly={submitted}
        basicSetup={{ lineNumbers: true, foldGutter: false }}
        theme="light"
      />
    </div>
  )
}

function runValidator(v: WriteCodeValidator, src: string): boolean {
  if (v.kind === 'contains') return src.includes(v.needle)
  if (v.kind === 'not-contains') return !src.includes(v.needle)
  // regex
  try {
    return new RegExp(v.pattern, v.flags ?? '').test(src)
  } catch {
    return false
  }
}

function gradeWriteCode(q: WriteCodeQuestion, source: string) {
  let score = 0
  const passed: string[] = []
  const failed: string[] = []
  const totalWeight = q.validators.reduce((sum, v) => sum + v.weight, 0) || 1
  for (const v of q.validators) {
    const ok = runValidator(v, source)
    if (ok) {
      score += v.weight
      if (v.weight > 0) passed.push(v.label)
    } else {
      if (v.weight > 0) failed.push(v.label)
    }
  }
  const normalized = Math.min(1, score / totalWeight)
  const correct = normalized >= 0.99
  return {
    score: normalized,
    max: 1,
    correct,
    hint: correct
      ? 'All checks passed.'
      : failed.length
      ? `Missing: ${failed.join(' · ')}`
      : 'Almost — review the sample answer below.',
    passed,
    failed,
  }
}

// --- Memory Diagram -----------------------------------------------------

function MemoryDiagramAnswer({
  q,
  guess,
  revealed,
  onGuessChange,
}: {
  q: MemoryDiagramQuestion
  guess: string
  revealed: boolean
  onGuessChange: (s: string) => void
}) {
  // Run the interpreter only on reveal — avoids paying the cost while
  // the student is still tracing on paper.
  const snapshots = useMemo<Snapshot[]>(() => {
    if (!revealed) return []
    try {
      return run(q.program)
    } catch (e) {
      console.error('Memory diagram interpreter error', e)
      return []
    }
  }, [q.program, revealed])

  const [step, setStep] = useState(0)
  const stepIdx = Math.min(step, Math.max(0, snapshots.length - 1))
  const snapshot = snapshots[stepIdx] ?? null

  return (
    <div className="md-answer">
      <CodeBlock code={q.program} />
      <label className="md-output-field">
        <span className="evaluate-label">Predicted output</span>
        <textarea
          className="md-output-input"
          rows={4}
          value={guess}
          disabled={revealed}
          placeholder="Write the printed output you traced on paper, line by line."
          onChange={(e) => onGuessChange(e.target.value)}
        />
      </label>
      {revealed && (
        <div className="md-reveal">
          <div className="md-reveal-row">
            <strong>Expected output:</strong>
            <pre className="md-expected">{q.expectedOutput}</pre>
          </div>
          <div className="md-canvas-wrap">
            <DiagramCanvas snapshot={snapshot} />
          </div>
          {snapshots.length > 0 && (
            <>
              <Timeline snapshots={snapshots} current={stepIdx} onSelect={setStep} />
              <StepControl
                total={snapshots.length}
                current={stepIdx}
                onChange={setStep}
                autoSpeedMs={700}
                showProgress
              />
            </>
          )}
        </div>
      )}
    </div>
  )
}

function gradeMemoryDiagram(q: MemoryDiagramQuestion, guess: string) {
  const norm = (s: string) =>
    s
      .trim()
      .replace(/\r\n/g, '\n')
      .split('\n')
      .map((l) => l.trim())
      .filter(Boolean)
      .join('\n')
  const correct = norm(guess) === norm(q.expectedOutput)
  return {
    score: correct ? 1 : 0,
    max: 1,
    correct,
    hint: correct ? 'Output matches.' : `Expected: ${q.expectedOutput.replace(/\n/g, ' ⏎ ')}`,
  }
}

// --- Per-question state union -------------------------------------------

type QState =
  | { kind: 'mcq'; selected: number | null }
  | { kind: 'evaluate'; value: string; type: string }
  | { kind: 'identify-lines'; selected: Set<number> }
  | { kind: 'write-code'; source: string }
  | { kind: 'memory-diagram'; guess: string }

function defaultState(q: Question): QState {
  switch (q.type) {
    case 'mcq':
      return { kind: 'mcq', selected: null }
    case 'evaluate':
      return { kind: 'evaluate', value: '', type: '' }
    case 'identify-lines':
      return { kind: 'identify-lines', selected: new Set() }
    case 'write-code':
      return { kind: 'write-code', source: q.template ?? '' }
    case 'memory-diagram':
      return { kind: 'memory-diagram', guess: '' }
  }
}

type GradeResult = {
  score: number
  max: number
  correct: boolean
  hint: string
  partial?: string[]
  passed?: string[]
  failed?: string[]
}

// --- Main component -----------------------------------------------------

export function QuizPractice() {
  const [topic, setTopic] = useState<Topic>('types-expressions')
  const [questionIdx, setQuestionIdx] = useState(0)
  // States and submission tracking are keyed by question id so switching
  // topics back and forth doesn't wipe in-progress answers.
  const [states, setStates] = useState<Record<string, QState>>({})
  const [submitted, setSubmitted] = useState<Record<string, GradeResult>>({})

  const topicQuestions = useMemo(() => QUIZ_BANK.filter((q) => q.topic === topic), [topic])
  const counts = useMemo(() => {
    const out: Record<Topic, number> = {} as Record<Topic, number>
    for (const t of TOPIC_ORDER) out[t] = 0
    for (const q of QUIZ_BANK) out[q.topic] = (out[q.topic] ?? 0) + 1
    return out
  }, [])

  const q = topicQuestions[questionIdx]
  const state = q ? states[q.id] ?? defaultState(q) : null
  const grade = q ? submitted[q.id] : undefined
  const isSubmitted = grade !== undefined

  const setState = (next: QState) => {
    if (!q) return
    setStates((prev) => ({ ...prev, [q.id]: next }))
  }

  const handleSubmit = () => {
    if (!q || !state) return
    let g: GradeResult
    switch (q.type) {
      case 'mcq':
        g = gradeMCQ(q, (state as { kind: 'mcq'; selected: number | null }).selected)
        break
      case 'evaluate':
        g = gradeEvaluate(q, state as { value: string; type: string; kind: 'evaluate' })
        break
      case 'identify-lines':
        g = gradeIdentifyLines(q, (state as { kind: 'identify-lines'; selected: Set<number> }).selected)
        break
      case 'write-code':
        g = gradeWriteCode(q, (state as { kind: 'write-code'; source: string }).source)
        break
      case 'memory-diagram':
        g = gradeMemoryDiagram(q, (state as { kind: 'memory-diagram'; guess: string }).guess)
        break
    }
    setSubmitted((prev) => ({ ...prev, [q.id]: g }))
  }

  const handleNext = () => setQuestionIdx((i) => Math.min(i + 1, topicQuestions.length - 1))
  const handlePrev = () => setQuestionIdx((i) => Math.max(i - 1, 0))
  const handleSwitchTopic = (t: Topic) => {
    setTopic(t)
    setQuestionIdx(0)
  }

  return (
    <div className="quiz-practice">
      <aside className="topic-sidebar">
        <div className="topic-sidebar-title">Topics</div>
        <ul>
          {TOPIC_ORDER.map((t) => {
            const meta = TOPIC_META[t]
            const isActive = t === topic
            const submittedInTopic = QUIZ_BANK.filter((q) => q.topic === t && submitted[q.id]).length
            return (
              <li key={t}>
                <button
                  type="button"
                  className={`topic-row${isActive ? ' active' : ''}`}
                  onClick={() => handleSwitchTopic(t)}
                >
                  <span className="topic-row-label">{meta.label}</span>
                  <span className="topic-row-count">
                    {submittedInTopic}/{counts[t]}
                  </span>
                </button>
              </li>
            )
          })}
        </ul>
      </aside>

      <section className="question-pane">
        {q && state ? (
          <>
            <div className="question-header">
              <div className="question-meta">
                <span className="question-number">
                  Question {shortLabel(q.source, questionIdx)}
                </span>
                {q.source && <span className="question-source">{q.source}</span>}
              </div>
              <div className="question-progress">
                {questionIdx + 1} / {topicQuestions.length}
              </div>
            </div>

            <p className="question-prompt">{q.prompt}</p>
            {q.code && q.type !== 'identify-lines' && q.type !== 'memory-diagram' && (
              <CodeBlock code={q.code} />
            )}

            <div className="answer-area">
              {q.type === 'mcq' && state.kind === 'mcq' && (
                <MCQAnswer
                  q={q}
                  selected={state.selected}
                  submitted={isSubmitted}
                  onChange={(n) => setState({ kind: 'mcq', selected: n })}
                />
              )}
              {q.type === 'evaluate' && state.kind === 'evaluate' && (
                <EvaluateAnswer
                  q={q}
                  state={state}
                  submitted={isSubmitted}
                  onChange={(s) => setState({ kind: 'evaluate', ...s })}
                />
              )}
              {q.type === 'identify-lines' && state.kind === 'identify-lines' && (
                <IdentifyLinesAnswer
                  q={q}
                  selected={state.selected}
                  submitted={isSubmitted}
                  onToggle={(n) => {
                    const next = new Set(state.selected)
                    if (next.has(n)) next.delete(n)
                    else next.add(n)
                    setState({ kind: 'identify-lines', selected: next })
                  }}
                />
              )}
              {q.type === 'write-code' && state.kind === 'write-code' && (
                <WriteCodeAnswer
                  source={state.source}
                  submitted={isSubmitted}
                  onChange={(s) => setState({ kind: 'write-code', source: s })}
                />
              )}
              {q.type === 'memory-diagram' && state.kind === 'memory-diagram' && (
                <MemoryDiagramAnswer
                  q={q}
                  guess={state.guess}
                  revealed={isSubmitted}
                  onGuessChange={(s) => setState({ kind: 'memory-diagram', guess: s })}
                />
              )}
            </div>

            <div className="question-controls">
              <button type="button" className="quiz-btn ghost" onClick={handlePrev} disabled={questionIdx === 0}>
                ← Prev
              </button>
              {!isSubmitted ? (
                <button type="button" className="quiz-btn primary" onClick={handleSubmit}>
                  Submit
                </button>
              ) : (
                <button
                  type="button"
                  className="quiz-btn ghost"
                  onClick={() => {
                    setSubmitted((prev) => {
                      const next = { ...prev }
                      delete next[q.id]
                      return next
                    })
                    setStates((prev) => ({ ...prev, [q.id]: defaultState(q) }))
                  }}
                >
                  Try again
                </button>
              )}
              <button
                type="button"
                className="quiz-btn primary"
                onClick={handleNext}
                disabled={questionIdx >= topicQuestions.length - 1}
              >
                Next →
              </button>
            </div>

            {grade && (
              <div className={`result-card ${grade.correct ? 'result-correct' : 'result-wrong'}`}>
                <div className="result-summary">
                  <span className="result-icon">{grade.correct ? '✓' : '✗'}</span>
                  <span className="result-score">
                    {(grade.score * 100).toFixed(0)}%
                  </span>
                  <span className="result-hint">{grade.hint}</span>
                </div>
                {grade.partial && grade.partial.length > 0 && (
                  <ul className="result-partial">
                    {grade.partial.map((p, i) => (
                      <li key={i}>{p}</li>
                    ))}
                  </ul>
                )}
                {grade.passed && grade.passed.length > 0 && (
                  <details className="result-validators">
                    <summary>Passed checks ({grade.passed.length})</summary>
                    <ul>
                      {grade.passed.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </details>
                )}
                {grade.failed && grade.failed.length > 0 && (
                  <details className="result-validators" open>
                    <summary>Missing checks ({grade.failed.length})</summary>
                    <ul>
                      {grade.failed.map((p, i) => (
                        <li key={i}>{p}</li>
                      ))}
                    </ul>
                  </details>
                )}
                {q.type === 'mcq' && q.explanation && (
                  <div className="result-explain">{q.explanation}</div>
                )}
                {(q.type === 'write-code' || q.type === 'identify-lines') && (
                  <details className="result-sample" open={!grade.correct}>
                    <summary>Sample answer</summary>
                    <pre className="code-block">
                      {q.type === 'write-code'
                        ? q.sampleAnswer
                        : `Lines: ${q.answer.join(', ')}`}
                    </pre>
                  </details>
                )}
                {q.type === 'evaluate' && (
                  <div className="result-explain">
                    Sample: <code>{q.preferredValue}</code>
                    {!q.isError && <> · type <code>{q.preferredType}</code></>}
                  </div>
                )}
                {(q.type === 'evaluate' || q.type === 'write-code') && q.partialCreditRules && q.partialCreditRules.length > 0 && (
                  <details className="result-rubric">
                    <summary>Rubric notes (partial credit)</summary>
                    <ul>
                      {q.partialCreditRules.map((r, i) => (
                        <li key={i}>
                          {r.description}
                          {r.deduction > 0 && <span className="rubric-deduction"> (−{r.deduction})</span>}
                        </li>
                      ))}
                    </ul>
                  </details>
                )}
              </div>
            )}
          </>
        ) : (
          <div className="question-empty">No questions in this topic yet.</div>
        )}
      </section>
    </div>
  )
}
