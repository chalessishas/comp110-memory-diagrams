import React from 'react'
import './writing.css'

const DIMENSION_LABELS = {
  grammar:      'Grammar',
  mechanics:    'Mechanics',
  vocabulary:   'Vocabulary',
  organization: 'Organization',
  development:  'Development',
  style:        'Style',
}

const getTitle = (overall) => {
  if (overall >= 4) return 'Excellent Work'
  if (overall >= 3) return 'Good Effort'
  return 'Keep Practicing'
}

const WritingResult = ({ score, userText, sampleResponse, sampleScore, taskType, onRetry, onBack }) => {
  const pct = Math.round((score.overall / 5) * 100)
  const title = getTitle(score.overall)

  return (
    <div style={{
      minHeight: '100vh', background: '#FAFAF8',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '48px 24px 80px' }}>

        {/* Score Ring */}
        <div style={{ textAlign: 'center', marginBottom: 40, animation: 'fadeUp 0.6s ease-out' }}>
          <div style={{
            width: 140, height: 140, borderRadius: '50%',
            background: `conic-gradient(#D4A574 ${pct * 3.6}deg, #EDE8E0 0deg)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 20px',
          }}>
            <div style={{
              width: 116, height: 116, borderRadius: '50%', background: '#FAFAF8',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            }}>
              <span style={{
                fontFamily: "'Instrument Serif', Georgia, serif",
                fontSize: 44, color: '#2D2A26', lineHeight: 1,
              }}>
                {score.overall}
              </span>
              <span style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 12, color: '#ADA899', marginTop: 2,
              }}>
                /5
              </span>
            </div>
          </div>

          <h2 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 28, color: '#2D2A26', fontWeight: 400, marginBottom: 0,
          }}>
            {title}
          </h2>
        </div>

        {/* Dimension Bars */}
        <div style={{
          background: 'white', borderRadius: 14, border: '1px solid #EDE8E0',
          padding: '24px 28px', marginBottom: 20,
          animation: 'fadeUp 0.5s ease-out 0.1s both',
        }}>
          <p style={{
            fontSize: 16, fontWeight: 700, color: '#2D2A26', marginBottom: 20,
          }}>
            Score Breakdown
          </p>

          {Object.entries(score.breakdown).map(([key, dim]) => {
            const pctVal = Math.round((dim.score || 0) * 100)
            const errors = dim.errors || []
            return (
              <div key={key} style={{ marginBottom: errors.length > 0 ? 16 : 12 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                  <span style={{
                    fontSize: 13, color: '#6B6560', width: 100, flexShrink: 0,
                  }}>
                    {DIMENSION_LABELS[key] || key}
                  </span>
                  <div className="score-bar-track" style={{ flex: 1 }}>
                    <div
                      className="score-bar-fill"
                      style={{ width: `${pctVal}%` }}
                    />
                  </div>
                  <span style={{
                    fontSize: 12, color: '#8A8477', width: 36, textAlign: 'right', flexShrink: 0,
                  }}>
                    {pctVal}%
                  </span>
                </div>
                {errors.slice(0, 2).map((err, i) => (
                  <p key={i} style={{
                    fontSize: 11, color: '#b06060', margin: '4px 0 0 112px', lineHeight: 1.5,
                  }}>
                    {err}
                  </p>
                ))}
              </div>
            )
          })}
        </div>

        {/* Suggestions */}
        {score.suggestions && score.suggestions.length > 0 && (
          <div style={{
            marginBottom: 20, animation: 'fadeUp 0.5s ease-out 0.15s both',
          }}>
            <p style={{
              fontSize: 16, fontWeight: 700, color: '#2D2A26', marginBottom: 12,
            }}>
              Suggestions for Improvement
            </p>
            {score.suggestions.map((tip, i) => (
              <div key={i} style={{
                background: 'rgba(212,165,116,0.04)',
                border: '1px solid rgba(212,165,116,0.15)',
                borderRadius: 10, padding: '14px 16px',
                marginBottom: 8,
              }}>
                <p style={{
                  fontSize: 13, color: '#6B5D4D', margin: 0, lineHeight: 1.6,
                }}>
                  {tip}
                </p>
              </div>
            ))}
          </div>
        )}

        {/* Response Comparison */}
        <div style={{ marginBottom: 32, animation: 'fadeUp 0.5s ease-out 0.2s both' }}>
          <p style={{
            fontSize: 16, fontWeight: 700, color: '#2D2A26', marginBottom: 12,
          }}>
            Response Comparison
          </p>
          <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap' }}>
            <div style={{
              flex: '1 1 280px', background: 'white', borderRadius: 12,
              border: '1px solid #EDE8E0', padding: 20,
            }}>
              <p style={{
                fontSize: 11, fontWeight: 600, color: '#ADA899',
                textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 14,
              }}>
                Your Response
              </p>
              <p style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 13,
                color: '#2D2A26', lineHeight: 1.7, whiteSpace: 'pre-wrap', margin: 0,
              }}>
                {userText}
              </p>
            </div>
            <div style={{
              flex: '1 1 280px', background: 'white', borderRadius: 12,
              border: '1.5px solid rgba(90,154,110,0.3)', padding: 20,
            }}>
              <p style={{
                fontSize: 11, fontWeight: 600, color: '#5a9a6e',
                textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 14,
              }}>
                Sample Response (Score: {sampleScore}/5)
              </p>
              <p style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 13,
                color: '#2D2A26', lineHeight: 1.7, whiteSpace: 'pre-wrap', margin: 0,
              }}>
                {sampleResponse}
              </p>
            </div>
          </div>
        </div>

        {/* Action Buttons */}
        <div style={{ display: 'flex', gap: 12, justifyContent: 'center', flexWrap: 'wrap' }}>
          <button
            onClick={onRetry}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
              color: 'white', background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
              border: 'none', borderRadius: 10, padding: '12px 28px', cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(212,165,116,0.25)',
            }}
          >
            Try Again
          </button>
          <button
            onClick={onBack}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
              color: '#6B6560', background: 'white',
              border: '1.5px solid #E2DDD5', borderRadius: 10, padding: '12px 28px', cursor: 'pointer',
            }}
          >
            Back to Writing
          </button>
        </div>

      </div>
    </div>
  )
}

export default WritingResult
