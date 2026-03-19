import React, { useState, useRef, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import './writing.css'
import Timer from '../shared/Timer.jsx'
import { discussionPrompts } from './data/discussionData.js'

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
  const [response, setResponse] = useState(savedData.current?.response ?? '')
  const [timer, setTimer] = useState(savedData.current?.timer ?? TOTAL_TIME)
  const [paused, setPaused] = useState(false)
  const [showResult, setShowResult] = useState(false)

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
    setShowResult(true)
  }

  const handleRetry = () => {
    clearProg()
    setStarted(false)
    setResponse('')
    setTimer(TOTAL_TIME)
    setPaused(false)
    setShowResult(false)
    savedData.current = null
  }

  const wordCountColor = wordCount >= 120 ? '#5a9a6e' : '#b87333'

  // ─── LANDING ───
  if (!started) {
    const hasResume = !!savedData.current
    return (
      <div style={{
        minHeight: '100vh', background: '#FAFAF8',
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
            background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 32px',
            boxShadow: '0 4px 16px rgba(212,165,116,0.3)',
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
            </svg>
          </div>

          <h1 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 42, fontWeight: 400, color: '#2D2A26',
            letterSpacing: '-0.02em', lineHeight: 1.15, marginBottom: 12,
          }}>
            Academic Discussion
          </h1>
          <p style={{
            fontSize: 15, color: '#8A8477', lineHeight: 1.7, marginBottom: 12, fontWeight: 300,
          }}>
            1 prompt · 10 minutes · 120+ words
          </p>
          <p style={{
            fontSize: 13, color: '#ADA899', lineHeight: 1.7, marginBottom: 40,
          }}>
            Read the professor's question and two student responses, then contribute your own perspective to the discussion.
          </p>

          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button
              onClick={() => navigate('/writing')}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: '#6B6560', background: 'white',
                border: '1.5px solid #E2DDD5', borderRadius: 10, padding: '12px 24px',
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
                background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
                border: 'none', borderRadius: 10, padding: '12px 32px', cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(212,165,116,0.25)',
              }}
            >
              {hasResume ? 'Resume' : 'Start Practice'}
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ─── RESULT ───
  if (showResult) {
    return (
      <div style={{
        minHeight: '100vh', background: '#FAFAF8',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ maxWidth: 720, margin: '0 auto', padding: '40px 24px 80px' }}>
          {/* Score ring (placeholder) */}
          <div style={{ textAlign: 'center', marginBottom: 40, animation: 'fadeUp 0.6s ease-out' }}>
            <div style={{
              width: 120, height: 120, borderRadius: '50%',
              background: 'conic-gradient(#D4A574 0deg, #EDE8E0 0deg)',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              margin: '0 auto 24px',
              border: '3px solid #EDE8E0',
            }}>
              <div style={{
                width: 96, height: 96, borderRadius: '50%', background: '#FAFAF8',
                display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
              }}>
                <span style={{
                  fontFamily: "'Instrument Serif', Georgia, serif",
                  fontSize: 36, color: '#ADA899', lineHeight: 1,
                }}>—</span>
                <span style={{ fontSize: 11, color: '#ADA899', marginTop: 2 }}>pending</span>
              </div>
            </div>

            <h2 style={{
              fontFamily: "'Instrument Serif', Georgia, serif",
              fontSize: 28, color: '#2D2A26', marginBottom: 8, fontWeight: 400,
            }}>
              Response Submitted
            </h2>
            <p style={{ fontSize: 14, color: '#8A8477' }}>
              Automated scoring coming soon · {wordCount} words written
            </p>
          </div>

          {/* Your response */}
          <div style={{
            background: 'white', borderRadius: 14, border: '1.5px solid #EDE8E0',
            padding: 28, marginBottom: 20, animation: 'fadeUp 0.5s ease-out 0.1s both',
          }}>
            <p style={{
              fontSize: 11, fontWeight: 600, color: '#ADA899',
              textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 16,
            }}>
              Your Response
            </p>
            <pre style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#2D2A26',
              lineHeight: 1.8, whiteSpace: 'pre-wrap', margin: 0,
            }}>
              {response}
            </pre>
          </div>

          {/* Sample response */}
          <div style={{
            background: 'rgba(90,154,110,0.04)', borderRadius: 14,
            border: '1.5px solid rgba(90,154,110,0.2)',
            padding: 28, marginBottom: 32, animation: 'fadeUp 0.5s ease-out 0.2s both',
          }}>
            <p style={{
              fontSize: 11, fontWeight: 600, color: '#5a9a6e',
              textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 16,
            }}>
              Sample Response (Score: {prompt.sampleScore}/5)
            </p>
            <pre style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#2D2A26',
              lineHeight: 1.8, whiteSpace: 'pre-wrap', margin: 0,
            }}>
              {prompt.sampleResponse}
            </pre>
          </div>

          {/* Actions */}
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={handleRetry}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: 'white', background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
                border: 'none', borderRadius: 10, padding: '12px 24px', cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(212,165,116,0.25)',
              }}
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/writing')}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: '#6B6560', background: 'white',
                border: '1.5px solid #E2DDD5', borderRadius: 10, padding: '12px 24px', cursor: 'pointer',
              }}
            >
              Back to Writing
            </button>
          </div>
        </div>
      </div>
    )
  }

  // ─── TEST INTERFACE ───
  return (
    <div className="discussion-layout">
      {/* Sticky header */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 10,
        padding: '14px 20px',
        borderBottom: '1px solid #EDE8E0',
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
          fontSize: 13, fontWeight: 500, color: '#8A8477',
        }}>
          Academic Discussion
        </span>
      </div>

      {/* Scrollable content */}
      <div style={{ padding: '32px', maxWidth: 800, margin: '0 auto', width: '100%', boxSizing: 'border-box' }}>

        {/* Professor card */}
        <div style={{
          background: 'rgba(212,165,116,0.04)',
          borderLeft: '3px solid #D4A574',
          borderRadius: 12,
          padding: '20px 24px',
          marginBottom: 24,
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 14 }}>
            <div style={{
              width: 42, height: 42, borderRadius: '50%',
              background: '#D4A574',
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
              fontSize: 14, fontWeight: 700, color: '#2D2A26',
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
              border: '1px solid #EDE8E0',
              borderRadius: 12,
              padding: '16px 20px',
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                <div style={{
                  width: 36, height: 36, borderRadius: '50%',
                  background: i === 0 ? '#E8D5C4' : '#C4D5E8',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <span style={{
                    fontFamily: "'DM Sans', sans-serif",
                    fontSize: 14, fontWeight: 700, color: '#2D2A26',
                  }}>
                    {student.name.charAt(0)}
                  </span>
                </div>
                <span style={{
                  fontFamily: "'DM Sans', sans-serif",
                  fontSize: 13, fontWeight: 700, color: '#2D2A26',
                }}>
                  {student.name}
                </span>
              </div>
              <p style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 13, lineHeight: 1.7, color: '#6B6560', margin: 0,
              }}>
                {student.opinion}
              </p>
            </div>
          ))}
        </div>

        {/* Divider */}
        <div style={{ borderTop: '1px solid #EDE8E0', margin: '24px 0' }} />

        {/* Your response */}
        <div>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 14, fontWeight: 700, color: '#2D2A26', marginBottom: 12,
          }}>
            Your Response
          </p>
          <textarea
            value={response}
            onChange={e => setResponse(e.target.value)}
            placeholder="Write your response here..."
            style={{
              width: '100%', minHeight: 200,
              border: '1.5px solid #E2DDD5', borderRadius: 12,
              padding: 16, resize: 'vertical',
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.8,
              color: '#2D2A26', background: 'white',
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
              onClick={handleSubmit}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: 'white',
                background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
                border: 'none', borderRadius: 10, padding: '10px 28px', cursor: 'pointer',
                boxShadow: '0 4px 12px rgba(212,165,116,0.25)',
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
