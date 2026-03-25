import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { colors, fonts, shadows } from '../shared/theme'

function ModuleCard({ icon, title, details, onStart, accentColor }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onStart}
      style={{
        background: colors.white,
        border: `1.5px solid ${hovered ? (accentColor || colors.primary) : colors.border}`,
        borderRadius: 10,
        padding: 24,
        flex: '1 1 240px',
        maxWidth: 320,
        display: 'flex',
        flexDirection: 'column',
        gap: 14,
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        transform: hovered ? 'translateY(-1px)' : 'none',
        boxShadow: hovered ? shadows.cardHover : shadows.card,
      }}
    >
      <div style={{
        width: 40, height: 40, borderRadius: 10,
        background: accentColor || colors.primary,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="white" opacity="0.9">
          <path d={icon} />
        </svg>
      </div>

      <div>
        <div style={{ fontFamily: fonts.heading, fontSize: 20, color: colors.text, marginBottom: 6 }}>
          {title}
        </div>
        {details.map((d, i) => (
          <div key={i} style={{ fontFamily: fonts.body, fontSize: 12, color: colors.textMuted, lineHeight: 1.6 }}>
            {d}
          </div>
        ))}
      </div>

      <div style={{
        marginTop: 'auto', paddingTop: 8,
        fontSize: 13, fontWeight: 600, color: accentColor || colors.primary,
        display: 'flex', alignItems: 'center', gap: 4,
      }}>
        Start practice
        <span style={{ fontSize: 16 }}>&#8250;</span>
      </div>
    </div>
  )
}

export default function Home() {
  const navigate = useNavigate()
  useEffect(() => { document.title = 'TOEFL Practice' }, [])

  return (
    <div style={{ padding: '32px 40px', maxWidth: 900 }}>
      {/* Welcome header */}
      <div style={{ marginBottom: 32 }}>
        <h1 style={{
          fontFamily: fonts.heading, fontSize: 28, fontWeight: 700,
          color: colors.text, marginBottom: 6,
        }}>
          Welcome back
        </h1>
        <p style={{ fontFamily: fonts.body, fontSize: 14, color: colors.textMuted }}>
          Pick up where you left off, or start a new practice session.
        </p>
      </div>

      {/* Stats row */}
      <div style={{
        display: 'flex', gap: 12, marginBottom: 32, flexWrap: 'wrap',
      }}>
        {[
          { label: 'Practice Sets', value: '3' },
          { label: 'Total Questions', value: '30+' },
          { label: 'Writing Tasks', value: '3 types' },
          { label: 'Completed', value: '0' },
        ].map((s, i) => (
          <div key={i} style={{
            flex: '1 1 120px', padding: '14px 16px',
            background: 'white', borderRadius: 8,
            border: '1px solid #eee',
          }}>
            <div style={{
              fontSize: 22, fontWeight: 700, color: colors.primary,
              fontFamily: fonts.body, marginBottom: 2,
            }}>{s.value}</div>
            <div style={{
              fontSize: 10, color: '#aaa', textTransform: 'uppercase',
              letterSpacing: '0.05em', fontFamily: fonts.body,
            }}>{s.label}</div>
          </div>
        ))}
      </div>

      {/* Reading section */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <div style={{ width: 3, height: 16, borderRadius: 2, background: colors.primary }} />
          <h2 style={{ fontSize: 15, fontWeight: 700, color: colors.text, fontFamily: fonts.body, margin: 0 }}>
            Reading
          </h2>
        </div>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <ModuleCard
            icon="M4 4h16v2H4zM4 8h10v2H4zM4 12h16v2H4zM4 16h10v2H4z"
            title="Reading Practice"
            details={['Academic passages + Pack 6 modules', '10-20 questions per set', 'Vocabulary, inference, detail']}
            onStart={() => navigate('/reading')}
            accentColor="#00695c"
          />
        </div>
      </div>

      {/* Writing section */}
      <div style={{ marginBottom: 28 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 14 }}>
          <div style={{ width: 3, height: 16, borderRadius: 2, background: '#00897b' }} />
          <h2 style={{ fontSize: 15, fontWeight: 700, color: colors.text, fontFamily: fonts.body, margin: 0 }}>
            Writing
          </h2>
        </div>
        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
          <ModuleCard
            icon="M12 2a3 3 0 0 1 3 3 3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3zm7 9c0-2.5-4.5-4-7-4s-7 1.5-7 4v1h14v-1zM5 14v6h14v-6H5zm2 2h10v2H7v-2z"
            title="Build a Sentence"
            details={['Arrange word chips in order', '10 items, 7 min']}
            onStart={() => navigate('/writing/build-sentence')}
            accentColor="#00695c"
          />
          <ModuleCard
            icon="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"
            title="Write an Email"
            details={['Respond to a situation prompt', '130-140 words, 7 min']}
            onStart={() => navigate('/writing/email')}
            accentColor="#00897b"
          />
          <ModuleCard
            icon="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 11H7V9h2v2zm4 0h-2V9h2v2zm4 0h-2V9h2v2z"
            title="Academic Discussion"
            details={['Join a class discussion', '120+ words, 10 min']}
            onStart={() => navigate('/writing/discussion')}
            accentColor="#004d40"
          />
        </div>
      </div>

      {/* Tip */}
      <div style={{
        padding: '14px 16px', background: 'rgba(0,105,92,0.03)',
        border: '1px solid rgba(0,105,92,0.08)', borderRadius: 8,
        fontSize: 12, color: '#555', lineHeight: 1.7,
      }}>
        <span style={{ fontWeight: 600, color: '#00695c' }}>Tip: </span>
        Start with Reading to build vocabulary, then move to Writing to practice expressing ideas.
        Your saved vocabulary and common mistakes will appear in the Notebook panel on the left.
      </div>
    </div>
  )
}
