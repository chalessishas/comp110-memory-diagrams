import { useEffect, useRef, useState } from 'react'
import './StepControl.css'

type Props = {
  total: number
  current: number
  onChange: (step: number) => void
  disabled?: boolean
}

export function StepControl({ total, current, onChange, disabled }: Props) {
  const [playing, setPlaying] = useState(false)
  const timer = useRef<number | null>(null)

  useEffect(() => {
    if (!playing) return
    timer.current = window.setInterval(() => {
      onChange(Math.min(total - 1, current + 1))
    }, 700)
    return () => {
      if (timer.current !== null) window.clearInterval(timer.current)
    }
  }, [playing, current, total, onChange])

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
        onClick={() => onChange(Math.max(0, current - 1))}
        disabled={disabled || current === 0}
        aria-label="Previous step (left arrow)"
        title="Previous step (←)"
      >
        ◀ Prev
      </button>
      <span className="step-counter" aria-live="polite" aria-atomic="true">
        Step {total === 0 ? 0 : current + 1} / {total}
      </span>
      <button
        type="button"
        onClick={() => onChange(Math.min(total - 1, current + 1))}
        disabled={disabled || current >= total - 1}
        aria-label="Next step (right arrow)"
        title="Next step (→)"
      >
        Next ▶
      </button>
      <button
        type="button"
        onClick={() => setPlaying((p) => !p)}
        disabled={disabled || total === 0}
        className={playing ? 'playing' : ''}
        aria-label={playing ? 'Pause auto-play (space)' : 'Start auto-play (space)'}
        aria-pressed={playing}
        title={playing ? 'Pause (space)' : 'Auto-play (space)'}
      >
        {playing ? '⏸ Pause' : '▶ Auto'}
      </button>
    </div>
  )
}
