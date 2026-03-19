import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { colors, fonts } from '../shared/theme'

function TaskCard({ icon, title, details, tagColor, onStart }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: colors.white,
        border: `1px solid ${colors.border}`,
        borderRadius: 16,
        padding: 28,
        width: 220,
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        boxShadow: hovered ? '0 8px 32px rgba(0,0,0,0.1)' : '0 2px 8px rgba(0,0,0,0.06)',
      }}
    >
      <div style={{
        width: 44,
        height: 44,
        borderRadius: '50%',
        background: tagColor,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        {icon}
      </div>

      <div>
        <div style={{ fontFamily: fonts.heading, fontSize: 20, color: colors.text, marginBottom: 8 }}>
          {title}
        </div>
        {details.map((d, i) => (
          <div key={i} style={{ fontFamily: fonts.body, fontSize: 13, color: colors.textMuted, lineHeight: 1.6 }}>
            {d}
          </div>
        ))}
      </div>

      <button
        onClick={onStart}
        style={{
          marginTop: 'auto',
          background: colors.primaryGradient,
          color: colors.white,
          border: 'none',
          borderRadius: 10,
          padding: '10px 20px',
          fontFamily: fonts.body,
          fontSize: 14,
          fontWeight: 500,
          cursor: 'pointer',
          boxShadow: `0 4px 16px ${colors.primaryShadow}`,
          alignSelf: 'flex-start',
        }}
      >
        Start →
      </button>
    </div>
  )
}

export default function Writing() {
  const navigate = useNavigate()

  return (
    <div style={{
      minHeight: '100vh',
      background: colors.bg,
      padding: 24,
      position: 'relative',
    }}>
      {/* Back link */}
      <button
        onClick={() => navigate('/')}
        style={{
          position: 'absolute',
          top: 24,
          left: 24,
          background: 'none',
          border: 'none',
          fontFamily: fonts.body,
          fontSize: 14,
          color: colors.textMedium,
          cursor: 'pointer',
          padding: 0,
          display: 'flex',
          alignItems: 'center',
          gap: 4,
        }}
      >
        ← Back to Home
      </button>

      {/* Main content */}
      <div className="fadeUp" style={{
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        minHeight: '100vh',
        gap: 36,
      }}>
        <div style={{ textAlign: 'center' }}>
          <h1 style={{ fontFamily: fonts.heading, fontSize: 36, color: colors.text, margin: '0 0 8px', fontWeight: 400 }}>
            Writing Practice
          </h1>
          <p style={{ fontFamily: fonts.body, fontSize: 14, color: colors.textMuted, margin: 0 }}>
            Choose a task type
          </p>
        </div>

        <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', justifyContent: 'center' }}>
          <TaskCard
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M12 2a3 3 0 0 1 3 3 3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3zm7 9c0-2.5-4.5-4-7-4s-7 1.5-7 4v1h14v-1zM5 14v6h14v-6H5zm2 2h10v2H7v-2z"
                  fill="white" opacity="0.9" />
              </svg>
            }
            title="Build a Sentence"
            details={['10 items · 7 min', 'Grammar & word order']}
            tagColor="#b87333"
            onStart={() => navigate('/writing/build-sentence')}
          />
          <TaskCard
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"
                  fill="white" opacity="0.9" />
              </svg>
            }
            title="Write an Email"
            details={['1 prompt · 7 min', '130-140 words']}
            tagColor="#4a7fa5"
            onStart={() => navigate('/writing/email')}
          />
          <TaskCard
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 11H7V9h2v2zm4 0h-2V9h2v2zm4 0h-2V9h2v2z"
                  fill="white" opacity="0.9" />
              </svg>
            }
            title="Academic Discussion"
            details={['1 prompt · 10 min', '120+ words']}
            tagColor="#7a5fb0"
            onStart={() => navigate('/writing/discussion')}
          />
        </div>
      </div>
    </div>
  )
}
