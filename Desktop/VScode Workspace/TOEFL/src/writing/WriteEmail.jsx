import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './writing.css'
import Timer from '../shared/Timer.jsx'
import { emailPrompts } from './data/emailData.js'
import { scoreWriting } from './scorer/index.js'
import WritingResult from './WritingResult.jsx'

const STORAGE_KEY = 'toefl-writing-email'
const TOTAL_TIME = 420 // 7 minutes

const loadSaved = () => {
  try {
    const s = localStorage.getItem(STORAGE_KEY)
    if (s) return JSON.parse(s)
  } catch {}
  return null
}

const saveProg = (state) => {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)) } catch {}
}

const clearProg = () => {
  try { localStorage.removeItem(STORAGE_KEY) } catch {}
}

const countWords = (text) =>
  text.trim() === '' ? 0 : text.trim().split(/\s+/).filter(w => w.length > 0).length

const WriteEmail = () => {
  const navigate = useNavigate()
  const savedData = useRef(loadSaved())

  const [started, setStarted] = useState(!!savedData.current)
  const [promptIdx, setPromptIdx] = useState(savedData.current?.promptIdx ?? 0)

  useEffect(() => { document.title = 'Write an Email — TOEFL Practice' }, [])
  const [subject, setSubject] = useState(savedData.current?.subject ?? '')
  const [body, setBody] = useState(savedData.current?.body ?? '')
  const [timer, setTimer] = useState(savedData.current?.timer ?? TOTAL_TIME)
  const [paused, setPaused] = useState(false)
  const [showResult, setShowResult] = useState(false)
  const [scoreResult, setScoreResult] = useState(null)
  const [showConfirm, setShowConfirm] = useState(false)

  const prompt = emailPrompts[promptIdx]
  const wordCount = countWords(body)

  // Save progress whenever relevant state changes
  useEffect(() => {
    if (started && !showResult) {
      saveProg({ subject, body, timer, promptIdx })
    }
  }, [subject, body, timer, promptIdx, started, showResult])

  const handleStart = () => {
    setStarted(true)
    savedData.current = null
  }

  const handleSubmit = () => {
    clearProg()
    const fullText = `Dear ${prompt.recipient},\n\n${body}\n\nBest regards,\n[Your Name]`
    const result = scoreWriting(fullText, 'email')
    setScoreResult(result)
    setShowResult(true)
  }

  const handleRetry = () => {
    clearProg()
    setStarted(false)
    setSubject('')
    setBody('')
    setTimer(TOTAL_TIME)
    setPaused(false)
    setShowResult(false)
    setScoreResult(null)
    savedData.current = null
  }

  const wordCountColor = () => {
    if (wordCount < 80) return '#b87333'
    if (wordCount > 180) return '#b06060'
    return '#5a9a6e'
  }

  // ─── LANDING ───
  if (!started) {
    const hasResume = !!savedData.current
    return (
      <div style={{
        minHeight: '100vh', background: '#f5f5f5',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{
          textAlign: 'center', animation: 'fadeUp 0.8s ease-out',
          maxWidth: 480, padding: '0 24px',
        }}>
          {/* Icon */}
          <div style={{
            width: 56, height: 56, borderRadius: 16,
            background: '#00695c',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 32px',
            boxShadow: '0 4px 16px rgba(0,105,92,0.2)',
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <rect x="2" y="4" width="20" height="16" rx="2"/>
              <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
            </svg>
          </div>

          <h1 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 42, fontWeight: 400, color: '#1a1a1a',
            letterSpacing: '-0.02em', lineHeight: 1.15, marginBottom: 12,
          }}>
            Write an Email
          </h1>
          <p style={{
            fontSize: 15, color: '#888', lineHeight: 1.7, marginBottom: 12, fontWeight: 300,
          }}>
            1 prompt · 7 minutes · 130–140 words
          </p>
          <p style={{
            fontSize: 13, color: '#aaa', lineHeight: 1.7, marginBottom: 40,
          }}>
            Read the situation and goals, then write a professional email that addresses all three points.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button
              onClick={() => navigate('/writing')}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: '#555', background: 'white',
                border: '1.5px solid #ccc', borderRadius: 10, padding: '12px 24px',
                cursor: 'pointer',
              }}
            >
              ← Back
            </button>
            <button
              onClick={handleStart}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: 'white',
                background: '#00695c',
                border: 'none', borderRadius: 10, padding: '12px 32px', cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(0,105,92,0.2)',
              }}
            >
              {hasResume ? 'Resume' : 'Start Practice'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ─── CONFIRM MODAL ───
  const ConfirmModal = () => (
    <div className="confirm-overlay" onClick={() => setShowConfirm(false)}>
      <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
        <h3>Submit Email?</h3>
        <p>
          Word count: {wordCount} (target: 130–140)
          {wordCount < 80 && <><br />Your response is quite short. Consider adding more detail.</>}
        </p>
        <div className="confirm-actions">
          <button className="btn-cancel" onClick={() => setShowConfirm(false)}>Continue Writing</button>
          <button className="btn-confirm" onClick={() => { setShowConfirm(false); handleSubmit() }}>Submit</button>
        </div>
      </div>
    </div>
  )

  // ─── RESULT ───
  if (showResult) {
    return (
      <WritingResult
        score={scoreResult}
        userText={body}
        sampleResponse={prompt.sampleResponse}
        sampleScore={prompt.sampleScore}
        taskType="email"
        onRetry={handleRetry}
        onBack={() => navigate('/writing')}
      />
    )
  }

  // ─── TEST INTERFACE ───
  return (
    <div className="email-layout">
      {showConfirm && <ConfirmModal />}
      {/* Left: Prompt panel */}
      <div className="email-prompt-panel">
        {/* Panel header */}
        <div style={{
          padding: '14px 20px',
          borderBottom: '1px solid #ddd',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <Timer
            totalTime={timer}
            paused={paused}
            onTogglePause={() => setPaused(p => !p)}
            onTick={(t) => setTimer(t)}
            onTimeUp={handleSubmit}
          />
          <span style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 13, fontWeight: 500, color: '#888',
          }}>
            Write an Email
          </span>
        </div>

        {/* Panel content */}
        <div style={{ padding: '24px 20px', overflowY: 'auto', flex: 1 }}>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 11, fontWeight: 600, color: '#aaa',
            textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10,
          }}>
            Situation
          </p>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, color: '#4A4640', lineHeight: 1.8, marginBottom: 28,
          }}>
            {prompt.situation}
          </p>

          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 11, fontWeight: 600, color: '#aaa',
            textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 12,
          }}>
            In Your Email:
          </p>
          <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
            {prompt.goals.map((goal, i) => (
              <li key={i} style={{
                display: 'flex', alignItems: 'flex-start', gap: 10,
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 14, color: '#4A4640', lineHeight: 1.7, marginBottom: 10,
              }}>
                <span style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: '#00695c', flexShrink: 0, marginTop: 7,
                }} />
                {goal}
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Right: Editor panel */}
      <div className="email-editor-panel">
        {/* Subject line */}
        <div style={{
          padding: '16px 24px',
          borderBottom: '1px solid #ddd',
          display: 'flex', alignItems: 'center', gap: 12,
          flexShrink: 0,
        }}>
          <label style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 13, fontWeight: 600, color: '#aaa',
            whiteSpace: 'nowrap', flexShrink: 0,
          }}>
            Subject:
          </label>
          <input
            type="text"
            value={subject}
            onChange={e => setSubject(e.target.value)}
            placeholder="Enter email subject..."
            style={{
              flex: 1, fontFamily: "'DM Sans', sans-serif", fontSize: 14,
              color: '#1a1a1a', background: 'transparent',
              border: 'none', borderBottom: '1.5px solid #ccc',
              outline: 'none', padding: '4px 0',
            }}
          />
        </div>

        {/* Greeting */}
        <div style={{
          padding: '16px 24px 0',
          flexShrink: 0,
        }}>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, color: '#1a1a1a', fontStyle: 'italic',
            margin: 0,
          }}>
            Dear {prompt.recipient},
          </p>
        </div>

        {/* Body textarea */}
        <textarea
          value={body}
          onChange={e => setBody(e.target.value)}
          placeholder="Write your email here..."
          style={{
            flex: 1, fontFamily: "'DM Sans', sans-serif", fontSize: 14,
            color: '#1a1a1a', lineHeight: 1.8, background: 'transparent',
            border: 'none', borderBottom: '1.5px solid #ddd',
            outline: 'none', resize: 'none',
            padding: '12px 24px',
          }}
        />

        {/* Closing */}
        <div style={{
          padding: '12px 24px 0',
          flexShrink: 0,
        }}>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, color: '#1a1a1a', fontStyle: 'italic',
            margin: 0, marginBottom: 4,
          }}>
            Best regards,
          </p>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, color: '#aaa', fontStyle: 'italic',
            margin: 0,
          }}>
            [Your Name]
          </p>
        </div>

        {/* Word count + submit */}
        <div style={{
          padding: '14px 24px',
          borderTop: '1px solid #ddd',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          flexShrink: 0,
        }}>
          <span style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 13, fontWeight: 500,
            color: wordCountColor(),
          }}>
            Words: {wordCount} / 130–140
          </span>
          <button
            onClick={() => setShowConfirm(true)}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
              color: 'white',
              background: '#00695c',
              border: 'none', borderRadius: 10, padding: '10px 28px', cursor: 'pointer',
              boxShadow: '0 4px 12px rgba(0,105,92,0.2)',
            }}
          >
            Submit
          </button>
        </div>
      </div>
    </div>
  )
}

export default WriteEmail
