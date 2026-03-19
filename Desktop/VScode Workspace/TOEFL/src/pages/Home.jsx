import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { colors, fonts } from '../shared/theme'

function ModuleCard({ icon, title, details, onStart, hoverShadow }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      style={{
        background: colors.white,
        border: `1px solid ${colors.border}`,
        borderRadius: 16,
        padding: 32,
        width: 260,
        display: 'flex',
        flexDirection: 'column',
        gap: 16,
        cursor: 'pointer',
        transition: 'transform 0.2s ease, box-shadow 0.2s ease',
        transform: hovered ? 'translateY(-2px)' : 'translateY(0)',
        boxShadow: hovered
          ? `0 8px 32px ${hoverShadow || colors.primaryShadow}`
          : '0 2px 8px rgba(0,0,0,0.06)',
      }}
    >
      <div style={{
        width: 44,
        height: 44,
        borderRadius: '50%',
        background: colors.primaryGradient,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
      }}>
        {icon}
      </div>

      <div>
        <div style={{ fontFamily: fonts.heading, fontSize: 24, color: colors.text, marginBottom: 8 }}>
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
          transition: 'transform 0.2s ease',
          alignSelf: 'flex-start',
        }}
      >
        Start →
      </button>
    </div>
  )
}

export default function Home() {
  const navigate = useNavigate()

  return (
    <div style={{
      minHeight: '100vh',
      background: colors.bg,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      justifyContent: 'center',
      padding: 24,
    }}>
      <div className="fadeUp" style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 40 }}>
        {/* Header */}
        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12 }}>
          <div style={{
            width: 56,
            height: 56,
            borderRadius: 14,
            background: colors.primaryGradient,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            boxShadow: `0 4px 16px ${colors.primaryShadow}`,
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M12 2L14.5 9H22L16 13.5L18.5 20.5L12 16L5.5 20.5L8 13.5L2 9H9.5L12 2Z"
                fill="white" opacity="0.9" />
            </svg>
          </div>
          <h1 style={{ fontFamily: fonts.heading, fontSize: 42, color: colors.text, margin: 0, fontWeight: 400 }}>
            TOEFL Practice
          </h1>
          <p style={{ fontFamily: fonts.body, fontSize: 15, color: colors.textMuted, margin: 0 }}>
            Select a practice module
          </p>
        </div>

        {/* Cards */}
        <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap', justifyContent: 'center' }}>
          <ModuleCard
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M4 4h16v2H4zM4 8h10v2H4zM4 12h16v2H4zM4 16h10v2H4z" fill="white" opacity="0.9" />
              </svg>
            }
            title="Reading"
            details={['Practice passage with 10 questions', '20 minutes']}
            onStart={() => navigate('/reading')}
          />
          <ModuleCard
            icon={
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none">
                <path d="M3 17.25V21h3.75L17.81 9.94l-3.75-3.75L3 17.25zM20.71 7.04a1 1 0 0 0 0-1.41l-2.34-2.34a1 1 0 0 0-1.41 0l-1.83 1.83 3.75 3.75 1.83-1.83z"
                  fill="white" opacity="0.9" />
              </svg>
            }
            title="Writing"
            details={['3 Task Types', 'Build Sentence · Write Email · Discussion', '24 minutes']}
            onStart={() => navigate('/writing')}
          />
        </div>
      </div>
    </div>
  )
}
