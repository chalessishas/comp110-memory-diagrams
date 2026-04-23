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

  return (
    <div className="step-control">
      <button
        type="button"
        onClick={() => onChange(0)}
        disabled={disabled || current === 0}
        title="Go to start"
      >
        ⏮
      </button>
      <button
        type="button"
        onClick={() => onChange(Math.max(0, current - 1))}
        disabled={disabled || current === 0}
        title="Previous step"
      >
        ◀ Prev
      </button>
      <span className="step-counter">
        Step {total === 0 ? 0 : current + 1} / {total}
      </span>
      <button
        type="button"
        onClick={() => onChange(Math.min(total - 1, current + 1))}
        disabled={disabled || current >= total - 1}
        title="Next step"
      >
        Next ▶
      </button>
      <button
        type="button"
        onClick={() => setPlaying((p) => !p)}
        disabled={disabled || total === 0}
        className={playing ? 'playing' : ''}
        title={playing ? 'Pause auto-play' : 'Auto-play'}
      >
        {playing ? '⏸ Pause' : '▶ Auto'}
      </button>
    </div>
  )
}
