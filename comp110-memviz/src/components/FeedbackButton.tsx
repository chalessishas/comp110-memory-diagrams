import { useState } from 'react'
import { track } from '@vercel/analytics'
import './FeedbackButton.css'

// Floating bottom-right widget. Collapsed state is a small tab; opening it
// asks Yes / Not-really and then offers an optional 255-char note.
// Both the vote and the note are posted as Vercel Analytics custom events,
// so the data shows up in the Vercel dashboard with no separate backend.
// Hidden in ?embed=1 so iframe hosts don't get the widget on top of their
// page chrome.

type Phase = 'collapsed' | 'asking' | 'noting' | 'thanks'
type Vote = 'yes' | 'no'

export function FeedbackButton({ hidden }: { hidden?: boolean }) {
  const [phase, setPhase] = useState<Phase>('collapsed')
  const [vote, setVote] = useState<Vote | null>(null)
  const [note, setNote] = useState('')

  if (hidden) return null

  const castVote = (v: Vote) => {
    setVote(v)
    track('feedback_vote', { vote: v })
    setPhase('noting')
  }

  const submitNote = () => {
    const trimmed = note.trim().slice(0, 255)
    if (vote && trimmed.length > 0) {
      track('feedback_note', { vote, note: trimmed })
    }
    setNote('')
    setPhase('thanks')
    setTimeout(() => setPhase('collapsed'), 2400)
  }

  if (phase === 'collapsed') {
    return (
      <button
        type="button"
        className="fb-tab"
        onClick={() => setPhase('asking')}
        aria-label="Give feedback about this tool"
      >
        Useful?
      </button>
    )
  }

  return (
    <div className="fb-panel" role="dialog" aria-label="Feedback">
      <button
        type="button"
        className="fb-close"
        onClick={() => setPhase('collapsed')}
        aria-label="Close feedback"
      >
        ×
      </button>
      {phase === 'asking' && (
        <>
          <p className="fb-q">Was this helpful?</p>
          <div className="fb-btns">
            <button type="button" onClick={() => castVote('yes')}>Yes</button>
            <button type="button" onClick={() => castVote('no')}>Not really</button>
          </div>
        </>
      )}
      {phase === 'noting' && (
        <>
          <p className="fb-q">
            {vote === 'yes' ? 'Nice — anything missing?' : 'Sorry — what went wrong?'}
          </p>
          <textarea
            value={note}
            onChange={(e) => setNote(e.target.value)}
            placeholder="optional (255 chars)"
            rows={3}
            maxLength={255}
          />
          <div className="fb-btns">
            <button type="button" onClick={submitNote}>Send</button>
            <button type="button" className="fb-skip" onClick={() => setPhase('thanks')}>Skip</button>
          </div>
        </>
      )}
      {phase === 'thanks' && <p className="fb-thanks">Thanks!</p>}
    </div>
  )
}
