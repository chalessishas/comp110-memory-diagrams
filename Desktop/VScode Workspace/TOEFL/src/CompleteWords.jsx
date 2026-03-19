import React, { useState, useRef, useEffect } from 'react';

/**
 * Complete the Words — fill in missing letters in a paragraph.
 *
 * Props:
 *   section: { paragraph: Array<{ text } | { blank, prefix, answer }> }
 *   onComplete: (results: { correct, total }) => void
 */
const CompleteWords = ({ section, onComplete }) => {
  const blanks = section.paragraph.filter(seg => seg.blank !== undefined);
  const [inputs, setInputs] = useState(() => blanks.map(() => ''));
  const [submitted, setSubmitted] = useState(false);
  const inputRefs = useRef([]);

  useEffect(() => {
    if (inputRefs.current[0]) inputRefs.current[0].focus();
  }, []);

  const handleChange = (idx, value) => {
    const next = [...inputs];
    next[idx] = value;
    setInputs(next);
  };

  const handleKeyDown = (idx, e) => {
    if (e.key === 'Tab' || e.key === 'Enter') {
      e.preventDefault();
      const nextIdx = e.shiftKey ? idx - 1 : idx + 1;
      if (nextIdx >= 0 && nextIdx < blanks.length) {
        inputRefs.current[nextIdx]?.focus();
      }
    }
  };

  const handleSubmit = () => {
    setSubmitted(true);
    const correct = blanks.filter((b, i) => {
      const full = inputs[i].toLowerCase().trim();
      const expected = b.blank.toLowerCase().trim();
      return full === expected;
    }).length;
    if (onComplete) onComplete({ correct, total: blanks.length });
  };

  const allFilled = inputs.every(v => v.length > 0);

  let blankIdx = 0;

  return (
    <div style={{
      minHeight: '100vh', background: '#FAFAF8',
      display: 'flex', flexDirection: 'column', alignItems: 'center',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      {/* Header */}
      <div style={{
        width: '100%', padding: '18px 28px',
        borderBottom: '1px solid #EDE8E0', background: 'white',
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <div style={{
          width: 32, height: 32, borderRadius: 9,
          background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round">
            <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
            <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
          </svg>
        </div>
        <div>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#2D2A26' }}>Complete the Words</h2>
          <p style={{ fontSize: 11, color: '#ADA899', marginTop: 1 }}>{section.title}</p>
        </div>
      </div>

      {/* Instructions */}
      <div style={{
        maxWidth: 720, width: '100%', padding: '32px 24px 16px',
      }}>
        <h1 style={{
          fontFamily: "'Instrument Serif', Georgia, serif",
          fontSize: 24, fontWeight: 400, color: '#2D2A26',
          textAlign: 'center', marginBottom: 32,
        }}>
          Fill in the missing letters in the paragraph.
        </h1>

        {/* Paragraph with blanks */}
        <div style={{
          background: 'white', borderRadius: 14,
          border: '1px solid #EDE8E0', padding: '28px 32px',
          fontSize: 15, lineHeight: 2.4, color: '#4A4640',
        }}>
          {section.paragraph.map((seg, i) => {
            if (seg.text !== undefined) {
              return <span key={i}>{seg.text}</span>;
            }

            const idx = blankIdx++;
            const isCorrect = submitted && inputs[idx].toLowerCase().trim() === seg.blank.toLowerCase().trim();
            const isWrong = submitted && !isCorrect;

            return (
              <span key={i} style={{ whiteSpace: 'nowrap' }}>
                <span style={{ color: '#8A8477', fontWeight: 500 }}>{seg.prefix}</span>
                {submitted ? (
                  <span style={{
                    display: 'inline-block',
                    borderBottom: `2px solid ${isCorrect ? '#5a9a6e' : '#b06060'}`,
                    padding: '0 4px',
                    minWidth: 40,
                    color: isCorrect ? '#5a9a6e' : '#b06060',
                    fontWeight: 500,
                    background: isCorrect ? 'rgba(90,154,110,0.06)' : 'rgba(176,96,96,0.06)',
                    borderRadius: 4,
                  }}>
                    {inputs[idx] || '___'}
                    {isWrong && (
                      <span style={{ color: '#5a9a6e', marginLeft: 6, fontSize: 12 }}>
                        ({seg.blank})
                      </span>
                    )}
                  </span>
                ) : (
                  <input
                    ref={el => inputRefs.current[idx] = el}
                    type="text"
                    value={inputs[idx]}
                    onChange={e => handleChange(idx, e.target.value)}
                    onKeyDown={e => handleKeyDown(idx, e)}
                    placeholder={seg.blank.replace(/./g, '_')}
                    style={{
                      border: 'none',
                      borderBottom: '2px solid #D4A574',
                      background: 'rgba(212,165,116,0.04)',
                      outline: 'none',
                      fontSize: 15,
                      fontFamily: 'inherit',
                      color: '#2D2A26',
                      padding: '2px 4px',
                      width: Math.max(seg.blank.length * 10, 40),
                      borderRadius: 0,
                      transition: 'border-color 0.2s',
                    }}
                    onFocus={e => e.target.style.borderColor = '#C4956A'}
                    onBlur={e => e.target.style.borderColor = '#D4A574'}
                  />
                )}
              </span>
            );
          })}
        </div>

        {/* Score summary after submit */}
        {submitted && (
          <div style={{
            marginTop: 20, padding: '16px 20px', borderRadius: 10,
            background: 'rgba(212,165,116,0.06)',
            border: '1px solid rgba(212,165,116,0.15)',
            textAlign: 'center',
            animation: 'fadeUp 0.3s ease-out',
          }}>
            <span style={{ fontSize: 14, color: '#6B5D4D' }}>
              {blanks.filter((b, i) => inputs[i].toLowerCase().trim() === b.blank.toLowerCase().trim()).length}
              {' / '}
              {blanks.length} correct
            </span>
          </div>
        )}

        {/* Submit / Continue / keyboard hint */}
        <div style={{
          marginTop: 24, display: 'flex', justifyContent: 'center',
          gap: 12, flexWrap: 'wrap',
        }}>
          {!submitted ? (
            <>
              <button
                onClick={handleSubmit}
                disabled={!allFilled}
                style={{
                  fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                  color: 'white',
                  background: allFilled
                    ? 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)'
                    : '#D4CFC5',
                  border: 'none', borderRadius: 10,
                  padding: '12px 36px', cursor: allFilled ? 'pointer' : 'default',
                  boxShadow: allFilled ? '0 4px 16px rgba(212,165,116,0.25)' : 'none',
                  transition: 'all 0.2s ease',
                }}
              >
                Check Answers
              </button>
              <p style={{ width: '100%', textAlign: 'center', fontSize: 11, color: '#ADA899', marginTop: 4 }}>
                Press <span style={{
                  display: 'inline-block', padding: '1px 6px', background: '#f0ece6',
                  border: '1px solid #e2ddd5', borderRadius: 4, fontSize: 10, fontWeight: 600,
                }}>Tab</span> to jump between blanks
              </p>
            </>
          ) : onComplete && (
            <button
              onClick={() => {
                const correct = blanks.filter((b, i) => inputs[i].toLowerCase().trim() === b.blank.toLowerCase().trim()).length;
                onComplete({ correct, total: blanks.length });
              }}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: 'white',
                background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
                border: 'none', borderRadius: 10,
                padding: '12px 36px', cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(212,165,116,0.25)',
              }}
            >
              Continue
            </button>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompleteWords;
