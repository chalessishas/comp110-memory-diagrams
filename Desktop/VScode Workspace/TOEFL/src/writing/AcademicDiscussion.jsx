import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './writing.css'
import Timer from '../shared/Timer.jsx'
import { discussionPrompts } from './data/discussionData.js'
import { scoreWriting } from './scorer/index.js'
import WritingResult from './WritingResult.jsx'

const STORAGE_KEY = 'toefl-writing-discussion'
const TOTAL_TIME = 600 // 10 minutes

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

const AcademicDiscussion = () => {
  const navigate = useNavigate()
  const savedData = useRef(loadSaved())

  const [started, setStarted] = useState(!!savedData.current)
  const [promptIdx, setPromptIdx] = useState(savedData.current?.promptIdx ?? 0)

  useEffect(() => { document.title = 'Academic Discussion — TOEFL Practice' }, [])
  const [response, setResponse] = useState(savedData.current?.response ?? '')
  const [timer, setTimer] = useState(savedData.current?.timer ?? TOTAL_TIME)
  const [paused, setPaused] = useState(false)
  const [showResult, setShowResult] = useState(false)
  const [scoreResult, setScoreResult] = useState(null)

  const prompt = discussionPrompts[promptIdx]
  const wordCount = countWords(response)

  useEffect(() => {
    if (started && !showResult) {
      saveProg({ response, timer, promptIdx })
    }
  }, [response, timer, promptIdx, started, showResult])

  const handleStart = () => {
    setStarted(true)
    savedData.current = null
  }

  const handleSubmit = () => {
    clearProg()
    const result = scoreWriting(response, 'discussion')
    setScoreResult(result)
    setShowResult(true)
  }

  const handleRetry = () => {
    clearProg()
    setStarted(false)
    setResponse('')
    setTimer(TOTAL_TIME)
    setPaused(false)
    setShowResult(false)
    setScoreResult(null)
    savedData.current = null
  }

  const [showConfirm, setShowConfirm] = useState(false)
  const wordCountColor = wordCount >= 120 ? '#5a9a6e' : '#b87333'

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
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>

          <h1 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 42, fontWeight: 400, color: '#1a1a1a',
            letterSpacing: '-0.02em', lineHeight: 1.15, marginBottom: 12,
          }}>
            Academic Discussion
          </h1>
          <p style={{
            fontSize: 15, color: '#888', lineHeight: 1.7, marginBottom: 12, fontWeight: 300,
          }}>
            1 prompt · 10 minutes · 120+ words
          </p>
          <p style={{
            fontSize: 13, color: '#aaa', lineHeight: 1.7, marginBottom: 40,
          }}>
            Read the professor's question and two student responses, then contribute your own perspective to the discussion.
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
        <h3>Submit Response?</h3>
        <p>
          Word count: {wordCount} (target: 120+)
          {wordCount < 60 && <><br />Your response is quite short. Consider expanding your argument.</>}
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
        userText={response}
        sampleResponse={prompt.sampleResponse}
        sampleScore={prompt.sampleScore}
        taskType="discussion"
        onRetry={handleRetry}
        onBack={() => navigate('/writing')}
      />
    )
  }

  // ─── TEST INTERFACE ───
  return (
    <div className="discussion-layout">
      {showConfirm && <ConfirmModal />}
      {/* Sticky header */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 10,
        padding: '14px 20px',
        borderBottom: '1px solid #ddd',
        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        background: 'white', flexShrink: 0,
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
          Academic Discussion
        </span>
      </div>

      {/* Scrollable content */}
      <div style={{ padding: '32px', maxWidth: 800, margin: '0 auto', width: '100%', boxSizing: 'border-box' }}>

        {/* Professor card */}
        <div style={{
          background: 'rgba(0,105,92,0.03)',
          borderLeft: '3px solid #00695c',
          borderRadius: 12,
          padding: '20px 24px',
          marginBottom: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
            <div style={{
              width: 42, height: 42, borderRadius: '50%',
              background: '#00695c',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              flexShrink: 0,
            }}>
              <span style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 16, fontWeight: 700, color: 'white',
              }}>
                {prompt.professor.name.charAt(0)}
              </span>
            </div>
            <span style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: 14, fontWeight: 700, color: '#1a1a1a',
            }}>
              {prompt.professor.name}
            </span>
          </div>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, lineHeight: 1.8, color: '#4A4640', margin: 0,
          }}>
            {prompt.professor.question}
          </p>
        </div>

        {/* Student cards */}
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap', marginBottom: 24 }}>
          {prompt.students.map((student, i) => (
            <div key={student.name} style={{
              flex: 1, minWidth: 250,
              background: 'white',
              border: '1px solid #ddd',
              borderRadius: 12,
              padding: '16px 20px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: '50%',
                  background: i === 0 ? '#e0f2f1' : '#b2dfdb',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <span style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: 14, fontWeight: 700, color: '#1a1a1a',
                  }}>
                    {student.name.charAt(0)}
                  </span>
                </div>
                <span style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 13, fontWeight: 700, color: '#1a1a1a',
                }}>
                  {student.name}
                </span>
              </div>
              <p style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 13, lineHeight: 1.7, color: '#555', margin: 0,
              }}>
                {student.opinion}
              </p>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div style={{ borderTop: '1px solid #ddd', margin: '24px 0' }} />

        {/* Your response */}
        <div>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, fontWeight: 700, color: '#1a1a1a', marginBottom: 12,
          }}>
            Your Response
          </p>
          <textarea
            value={response}
            onChange={e => setResponse(e.target.value)}
            placeholder="Write your response here..."
            style={{
              width: '100%', minHeight: 200,
              border: '1.5px solid #ccc', borderRadius: 12,
              padding: 16, resize: 'vertical',
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.8,
              color: '#1a1a1a', background: 'white',
              outline: 'none', boxSizing: 'border-box',
            }}
          />
          <div style={{
            display: 'flex', alignItems: 'center', justifyContent: 'space-between',
            marginTop: 12,
          }}>
            <span style={{
              fontFamily: "'DM Sans', sans-serif",
              fontSize: 13, fontWeight: 500,
              color: wordCountColor,
            }}>
              Words: {wordCount} / 120+
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
    </div>
  )
}

export default AcademicDiscussion
