import { useEffect, useRef } from 'react'
import '../App.css'

export default function Timer({ totalTime, paused, onTogglePause, onTick, onTimeUp }) {
  const onTickRef = useRef(onTick)
  const onTimeUpRef = useRef(onTimeUp)
  const timerRef = useRef(totalTime)

  useEffect(() => { onTickRef.current = onTick }, [onTick])
  useEffect(() => { onTimeUpRef.current = onTimeUp }, [onTimeUp])
  // Keep internal ref in sync with parent's timer value
  useEffect(() => { timerRef.current = totalTime }, [totalTime])

  useEffect(() => {
    if (paused || totalTime <= 0) return
    const id = setInterval(() => {
      const next = timerRef.current - 1
      timerRef.current = next
      onTickRef.current?.(next)
      if (next <= 0) {
        clearInterval(id)
        onTimeUpRef.current?.()
      }
    }, 1000)
    return () => clearInterval(id)
  }, [paused, totalTime <= 0])

  const minutes = Math.floor(totalTime / 60)
  const seconds = totalTime % 60
  const display = `${minutes}:${String(seconds).padStart(2, '0')}`
  const isLow = totalTime < 120

  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
      <button
        className="timer-btn"
        onClick={onTogglePause}
        style={{
          background: isLow ? 'rgba(176,96,96,0.08)' : 'rgba(212,165,116,0.08)',
          color: isLow ? '#b06060' : '#6B6560',
          border: `1px solid ${isLow ? 'rgba(176,96,96,0.2)' : '#E2DDD5'}`,
        }}
      >
        <span>{paused ? '▶' : '⏸'}</span>
        <span>{display}</span>
      </button>
      {paused && <span className="pause-badge">⏸ PAUSED</span>}
    </div>
  )
}
