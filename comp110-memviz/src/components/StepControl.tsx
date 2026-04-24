import { useEffect, useRef, useState } from 'react'
import './StepControl.css'

type Props = {
  total: number
  current: number
  onChange: (step: number) => void
  disabled?: boolean
  // Auto-play interval in ms. When omitted, defaults to 700ms. Wired to the
  // speed slider in App.tsx so students can slow down / speed up.
  autoSpeedMs?: number
  // When true, a slim progress bar under the step counter fills up during
  // the current auto-play interval. Purely informational — lets students
  // feel the cadence.
  showProgress?: boolean
}

export function StepControl({
  total,
  current,
  onChange,
  disabled,
  autoSpeedMs = 700,
  showProgress = false,
}: Props) {
  const [playing, setPlaying] = useState(false)
  const timer = useRef<number | null>(null)
  // Progress fraction in [0,1] for the *current* auto-play tick. Updated on a
  // rAF loop so it's smooth even at slow speeds; reset to 0 every time the
  // step advances. When not playing this stays 0 so the bar is flat/hidden.
  const [progress, setProgress] = useState(0)

  // Auto-play: advance one step every autoSpeedMs while `playing`. The
  // useEffect is re-created whenever current / speed changes so the cadence
  // always matches the latest speed setting, not a stale closure.
  useEffect(() => {
    if (!playing) return
    timer.current = window.setInterval(() => {
      onChange(Math.min(total - 1, current + 1))
    }, autoSpeedMs)
    return () => {
      if (timer.current !== null) window.clearInterval(timer.current)
    }
  }, [playing, current, total, onChange, autoSpeedMs])

  // Progress bar animation: independent rAF loop that fills a 0→1 ramp over
  // the current interval. Resets on each step change; stops when not playing
  // or when showProgress is off (the state update is harmless but we skip
  // the work to be tidy).
  useEffect(() => {
    if (!playing || !showProgress) {
      setProgress(0)
      return
    }
    const start = performance.now()
    let raf = 0
    const tick = (t: number) => {
      const p = Math.min(1, (t - start) / autoSpeedMs)
      setProgress(p)
      if (p < 1) raf = requestAnimationFrame(tick)
    }
    raf = requestAnimationFrame(tick)
    return () => cancelAnimationFrame(raf)
  }, [playing, showProgress, autoSpeedMs, current])

  useEffect(() => {
    if (current >= total - 1) setPlaying(false)
  }, [current, total])

  // Keyboard shortcuts: ← / → step backward / forward, Space toggles auto-play.
  // Only fires when focus is NOT inside the code editor (so typing space in
  // the source isn't hijacked).
  useEffect(() => {
    if (disabled) return
    const onKey = (e: KeyboardEvent) => {
      const target = e.target as HTMLElement | null
      const inEditor = target?.closest('.cm-editor') !== null
      if (inEditor) return
      if (e.key === 'ArrowLeft') {
        e.preventDefault()
        onChange(Math.max(0, current - 1))
      } else if (e.key === 'ArrowRight') {
        e.preventDefault()
        onChange(Math.min(total - 1, current + 1))
      } else if (e.key === ' ' && total > 0) {
        e.preventDefault()
        setPlaying((p) => !p)
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [current, total, disabled, onChange])

  return (
    <div className="step-control" role="toolbar" aria-label="Step navigation">
      <button
        type="button"
        onClick={() => onChange(0)}
        disabled={disabled || current === 0}
        aria-label="Go to first step"
        title="Go to start"
      >
        ⏮
      </button>
      <button
        type="button"
        className="with-kbd"
        onClick={() => onChange(Math.max(0, current - 1))}
        disabled={disabled || current === 0}
        aria-label="Previous step (left arrow)"
        title="Previous step (←)"
      >
        <span>◀ Prev</span>
        <kbd aria-hidden="true">←</kbd>
      </button>
      <div className="step-counter-wrap">
        <span className="step-counter" aria-live="polite" aria-atomic="true">
          Step {total === 0 ? 0 : current + 1} / {total}
        </span>
        {showProgress && playing && (
          <span
            className="step-progress"
            aria-hidden="true"
            style={{ transform: `scaleX(${progress})` }}
          />
        )}
      </div>
      <button
        type="button"
        className="with-kbd"
        onClick={() => onChange(Math.min(total - 1, current + 1))}
        disabled={disabled || current >= total - 1}
        aria-label="Next step (right arrow)"
        title="Next step (→)"
      >
        <span>Next ▶</span>
        <kbd aria-hidden="true">→</kbd>
      </button>
      <button
        type="button"
        className={`with-kbd${playing ? ' playing' : ''}`}
        onClick={() => setPlaying((p) => !p)}
        disabled={disabled || total === 0}
        aria-label={playing ? 'Pause auto-play (space)' : 'Start auto-play (space)'}
        aria-pressed={playing}
        title={playing ? 'Pause (space)' : 'Auto-play (space)'}
      >
        <span>{playing ? '⏸ Pause' : '▶ Auto'}</span>
        <kbd aria-hidden="true">Space</kbd>
      </button>
    </div>
  )
}
