import React, { useState, useRef, useEffect } from 'react';
import { colors, fonts } from './shared/theme';

const CompleteWords = ({ section, onComplete }) => {
  const blanks = section.paragraph.filter(seg => seg.blank !== undefined);
  const [inputs, setInputs] = useState(() => blanks.map(() => ''));
  const [activeBlank, setActiveBlank] = useState(null);
  const [submitted, setSubmitted] = useState(false);
  const inputRef = useRef(null);

  useEffect(() => {
    if (activeBlank !== null && inputRef.current) {
      inputRef.current.focus();
    }
  }, [activeBlank]);

  const handleBlankClick = (idx) => {
    if (submitted) return;
    setActiveBlank(idx);
  };

  const handleChange = (value) => {
    if (activeBlank === null) return;
    const next = [...inputs];
    next[activeBlank] = value;
    setInputs(next);
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Tab') {
      e.preventDefault();
      const next = e.shiftKey
        ? Math.max(0, (activeBlank ?? 0) - 1)
        : Math.min(blanks.length - 1, (activeBlank ?? 0) + 1);
      setActiveBlank(next);
    } else if (e.key === 'Enter') {
      if (activeBlank < blanks.length - 1) {
        setActiveBlank(activeBlank + 1);
      }
    }
  };

  const handleSubmit = () => {
    setSubmitted(true);
    setActiveBlank(null);
  };

  const allFilled = inputs.every(v => v.length > 0);

  const getScore = () => {
    return blanks.filter((b, i) =>
      inputs[i].toLowerCase().trim() === b.blank.toLowerCase().trim()
    ).length;
  };

  let blankIdx = 0;

  return (
    <div style={{ minHeight: '100%', background: 'white' }}>
      {/* Instruction title — red underline like real TOEFL */}
      <div style={{
        borderBottom: '3px solid #c62828',
        padding: '28px 60px 18px',
      }}>
        <h1 style={{
          fontFamily: "'Georgia', 'Times New Roman', serif",
          fontSize: 28,
          fontWeight: 700,
          color: '#1a1a1a',
          margin: 0,
          textAlign: 'center',
        }}>
          Fill in the missing letters in the paragraph.
        </h1>
      </div>

      {/* Paragraph with inline gray blocks */}
      <div style={{
        maxWidth: 1100,
        margin: '0 auto',
        padding: '50px 60px 40px',
      }}>
        <div style={{
          fontSize: 19,
          lineHeight: 2.6,
          color: '#1a1a1a',
          fontFamily: "'Georgia', 'Times New Roman', serif",
          letterSpacing: '0.01em',
        }}>
          {section.paragraph.map((seg, i) => {
            if (seg.text !== undefined) {
              return <span key={i}>{seg.text}</span>;
            }

            const idx = blankIdx++;
            const isActive = activeBlank === idx;
            const userInput = inputs[idx];
            const isCorrect = submitted && userInput.toLowerCase().trim() === seg.blank.toLowerCase().trim();
            const isWrong = submitted && !isCorrect;

            if (submitted) {
              return (
                <span key={i} style={{ whiteSpace: 'nowrap' }}>
                  <span>{seg.prefix}</span>
                  <span style={{
                    display: 'inline-block',
                    borderBottom: `2.5px solid ${isCorrect ? '#2e7d32' : '#c62828'}`,
                    background: isCorrect ? 'rgba(46,125,50,0.06)' : 'rgba(198,40,40,0.06)',
                    padding: '1px 4px',
                    borderRadius: 2,
                    color: isCorrect ? '#2e7d32' : '#c62828',
                    fontWeight: 600,
                    minWidth: seg.blank.length * 10,
                  }}>
                    {userInput || '___'}
                    {isWrong && (
                      <span style={{
                        color: '#2e7d32', fontSize: 15, marginLeft: 6,
                        fontWeight: 400,
                      }}> → {seg.blank}</span>
                    )}
                  </span>
                </span>
              );
            }

            return (
              <span key={i} style={{ whiteSpace: 'nowrap' }}>
                <span>{seg.prefix}</span>
                <span
                  onClick={() => handleBlankClick(idx)}
                  style={{
                    display: 'inline-block',
                    minWidth: Math.max(seg.blank.length * 11, 45),
                    padding: '2px 5px',
                    background: isActive ? '#c8c8c8' : '#d5d5d5',
                    borderRadius: 2,
                    cursor: 'pointer',
                    border: isActive ? '2px solid #00695c' : '1px solid #b0b0b0',
                    boxShadow: isActive ? '0 0 0 1px #00695c' : 'none',
                    transition: 'all 0.12s ease',
                    fontSize: 19,
                    color: userInput ? '#1a1a1a' : 'transparent',
                    fontWeight: 500,
                    lineHeight: 1.4,
                    fontFamily: "'Georgia', 'Times New Roman', serif",
                  }}
                >
                  {userInput || '\u00A0'.repeat(Math.max(seg.blank.length, 3))}
                </span>
              </span>
            );
          })}
        </div>

        {/* Hidden input for keyboard capture */}
        {activeBlank !== null && !submitted && (
          <input
            ref={inputRef}
            type="text"
            value={inputs[activeBlank] || ''}
            onChange={e => handleChange(e.target.value)}
            onKeyDown={handleKeyDown}
            onBlur={() => {}}
            aria-label={`Fill blank ${activeBlank + 1} of ${blanks.length}`}
            style={{
              position: 'fixed',
              left: -9999,
              top: -9999,
              opacity: 0,
            }}
            autoFocus
          />
        )}
      </div>

      {/* Bottom area */}
      <div style={{
        maxWidth: 1100,
        margin: '0 auto',
        padding: '0 60px 50px',
      }}>
        {/* Score after submit */}
        {submitted && (
          <div style={{
            padding: '16px 24px',
            borderRadius: 8,
            background: 'rgba(0,105,92,0.05)',
            border: '1.5px solid rgba(0,105,92,0.2)',
            textAlign: 'center',
            marginBottom: 24,
            animation: 'fadeUp 0.3s ease-out',
          }}>
            <span style={{
              fontSize: 17, color: '#00695c', fontWeight: 700,
              fontFamily: "'DM Sans', sans-serif",
            }}>
              {getScore()} / {blanks.length} correct
            </span>
          </div>
        )}

        {/* Actions */}
        <div style={{ display: 'flex', justifyContent: 'center', gap: 12 }}>
          {!submitted ? (
            <button
              onClick={handleSubmit}
              disabled={!allFilled}
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 15,
                fontWeight: 700,
                color: 'white',
                background: allFilled ? '#00695c' : '#bbb',
                border: 'none',
                borderRadius: 6,
                padding: '12px 40px',
                cursor: allFilled ? 'pointer' : 'default',
                transition: 'all 0.2s ease',
                letterSpacing: '0.02em',
              }}
            >
              Check Answers
            </button>
          ) : onComplete && (
            <button
              onClick={() => onComplete({ correct: getScore(), total: blanks.length })}
              style={{
                fontFamily: "'DM Sans', sans-serif",
                fontSize: 15,
                fontWeight: 700,
                color: 'white',
                background: '#00695c',
                border: 'none',
                borderRadius: 6,
                padding: '12px 40px',
                cursor: 'pointer',
                letterSpacing: '0.02em',
              }}
            >
              Continue →
            </button>
          )}
        </div>

        {/* Keyboard hint */}
        {!submitted && activeBlank !== null && (
          <p style={{
            textAlign: 'center',
            fontSize: 13,
            color: '#999',
            marginTop: 16,
            fontFamily: "'DM Sans', sans-serif",
          }}>
            Click gray blocks to type · <kbd style={{
              padding: '2px 6px', background: '#f0f0f0',
              border: '1px solid #ddd', borderRadius: 3, fontSize: 11,
              fontFamily: "'DM Sans', sans-serif",
            }}>Tab</kbd> to jump between blanks
          </p>
        )}

        {!submitted && activeBlank === null && (
          <p style={{
            textAlign: 'center',
            fontSize: 14,
            color: '#999',
            marginTop: 24,
            fontFamily: "'DM Sans', sans-serif",
          }}>
            Click on the gray blocks above to fill in the missing letters.
          </p>
        )}
      </div>
    </div>
  );
};

export default CompleteWords;
