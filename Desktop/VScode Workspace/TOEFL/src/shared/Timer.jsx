import { useState, useEffect, useRef } from 'react'
import '../App.css'

export default function Timer({ totalTime, onTimeUp, paused, onTogglePause, onTick }) {
  const [timer, setTimer] = useState(totalTime)
  const onTickRef = useRef(onTick)
  const onTimeUpRef = useRef(onTimeUp)

  useEffect(() => { onTickRef.current = onTick }, [onTick])
  useEffect(() => { onTimeUpRef.current = onTimeUp }, [onTimeUp])

  useEffect(() => {
    if (paused) return
    if (timer <= 0) {
      onTimeUpRef.current?.()
      return
    }
    const id = setInterval(() => {
      setTimer(prev => {
        const next = prev - 1
        onTickRef.current?.(next)
        if (next <= 0) {
          clearInterval(id)
          onTimeUpRef.current?.()
        }
        return next
      })
    }, 1000)
    return () => clearInterval(id)
  }, [paused, timer])

  const minutes = Math.floor(timer / 60)
  const seconds = timer % 60
  const display = `${minutes}:${String(seconds).padStart(2, '0')}`
  const isLow = timer < 120

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
