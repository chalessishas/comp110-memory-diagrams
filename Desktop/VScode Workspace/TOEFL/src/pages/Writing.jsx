import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { colors, fonts, shadows } from '../shared/theme'

function TaskCard({ icon, title, details, tagColor, onStart }) {
  const [hovered, setHovered] = useState(false)

  return (
    <div
      onMouseEnter={() => setHovered(true)}
      onMouseLeave={() => setHovered(false)}
      onClick={onStart}
      style={{
        background: colors.white,
        border: `1.5px solid ${hovered ? colors.primary : colors.border}`,
        borderRadius: 10,
        padding: 24,
        flex: '1 1 200px',
        maxWidth: 280,
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
        background: tagColor || colors.primary,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
      }}>
        <svg width="20" height="20" viewBox="0 0 24 24" fill="white" opacity="0.9">
          <path d={icon} />
        </svg>
      </div>

      <div>
        <div style={{ fontFamily: fonts.heading, fontSize: 18, color: colors.text, marginBottom: 6 }}>
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
        fontSize: 13, fontWeight: 600, color: tagColor || colors.primary,
      }}>
        Start &#8250;
      </div>
    </div>
  )
}

export default function Writing() {
  const navigate = useNavigate()
  useEffect(() => { document.title = 'Writing -- TOEFL Practice' }, [])

  return (
    <div style={{ padding: '32px 40px', maxWidth: 900 }}>
      <div style={{ marginBottom: 28 }}>
        <h1 style={{ fontFamily: fonts.heading, fontSize: 28, color: colors.text, marginBottom: 6, fontWeight: 700 }}>
          Writing Practice
        </h1>
        <p style={{ fontFamily: fonts.body, fontSize: 14, color: colors.textMuted }}>
          Choose a task type to begin
        </p>
      </div>

      <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
        <TaskCard
          icon="M12 2a3 3 0 0 1 3 3 3 3 0 0 1-3 3 3 3 0 0 1-3-3 3 3 0 0 1 3-3zm7 9c0-2.5-4.5-4-7-4s-7 1.5-7 4v1h14v-1zM5 14v6h14v-6H5zm2 2h10v2H7v-2z"
          title="Build a Sentence"
          details={['10 items, 7 min', 'Grammar and word order']}
          tagColor="#00695c"
          onStart={() => navigate('/writing/build-sentence')}
        />
        <TaskCard
          icon="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4-8 5-8-5V6l8 5 8-5v2z"
          title="Write an Email"
          details={['1 prompt, 7 min', '130-140 words']}
          tagColor="#00897b"
          onStart={() => navigate('/writing/email')}
        />
        <TaskCard
          icon="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zM9 11H7V9h2v2zm4 0h-2V9h2v2zm4 0h-2V9h2v2z"
          title="Academic Discussion"
          details={['1 prompt, 10 min', '120+ words']}
          tagColor="#004d40"
          onStart={() => navigate('/writing/discussion')}
        />
      </div>
    </div>
  )
}
