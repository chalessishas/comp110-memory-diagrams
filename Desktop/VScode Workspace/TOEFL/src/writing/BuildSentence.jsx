import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import './writing.css';
import { buildSentenceItems } from './data/buildSentenceData.js';

const STORAGE_KEY = 'toefl-writing-build-sentence';
const TOTAL_TIME = 7 * 60;
const TOTAL_ITEMS = buildSentenceItems.length;

const loadSaved = () => {
  try {
    const s = localStorage.getItem(STORAGE_KEY);
    if (s) return JSON.parse(s);
  } catch {}
  return null;
};

const saveProg = (state) => {
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch {}
};

const clearProg = () => {
  try { localStorage.removeItem(STORAGE_KEY); } catch {}
};

const displayWord = (w) => w.replace(/\(\d+\)$/, '');

const BuildSentence = () => {
  const navigate = useNavigate();
  const savedData = useRef(loadSaved());

  const [started, setStarted] = useState(!!savedData.current);
  const [currentItem, setCurrentItem] = useState(savedData.current?.currentItem || 0);

  useEffect(() => { document.title = 'Build a Sentence — TOEFL Practice' }, []);
  const [answers, setAnswers] = useState(savedData.current?.answers || {});
  const [timer, setTimer] = useState(savedData.current?.timer || TOTAL_TIME);
  const [paused, setPaused] = useState(false);
  const [showResult, setShowResult] = useState(false);
  const [showReview, setShowReview] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [fadeIn, setFadeIn] = useState(true);

  // Timer countdown
  useEffect(() => {
    if (!started || showResult || paused || timer <= 0) return;
    const interval = setInterval(() => setTimer(t => t - 1), 1000);
    return () => clearInterval(interval);
  }, [started, showResult, paused, timer]);

  // Auto-submit when timer hits 0
  useEffect(() => {
    if (timer === 0 && started && !showResult) {
      handleSubmit();
    }
  }, [timer]);

  // Save progress
  useEffect(() => {
    if (started && !showResult) {
      saveProg({ currentItem, answers, timer });
    }
  }, [currentItem, answers, timer, started, showResult]);

  // Fade animation on item change
  useEffect(() => {
    setFadeIn(false);
    const t = setTimeout(() => setFadeIn(true), 50);
    return () => clearTimeout(t);
  }, [currentItem, showResult, showReview]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKey = (e) => {
      if (e.code === 'Space' && started && !showResult) {
        e.preventDefault();
        setPaused(p => !p);
      }
      if (e.code === 'ArrowRight' && started && !showResult && !showConfirm) {
        if (currentItem < TOTAL_ITEMS - 1) goToItem(currentItem + 1);
      }
      if (e.code === 'ArrowLeft' && started && !showResult && !showConfirm) {
        if (currentItem > 0) goToItem(currentItem - 1);
      }
    };
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, [started, showResult, showConfirm, currentItem]);

  const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  const goToItem = (idx) => {
    setCurrentItem(idx);
  };

  const getCurrentPlaced = () => answers[currentItem] || [];

  const handlePlaceWord = (word) => {
    const item = buildSentenceItems[currentItem];
    const placed = getCurrentPlaced();
    if (placed.includes(word)) return;
    if (placed.length >= item.correctOrder.length) return;
    setAnswers(prev => ({ ...prev, [currentItem]: [...placed, word] }));
  };

  const handleRemoveWord = (idx) => {
    const placed = getCurrentPlaced();
    const updated = placed.filter((_, i) => i !== idx);
    setAnswers(prev => ({ ...prev, [currentItem]: updated }));
  };

  const handleReset = () => {
    setAnswers(prev => ({ ...prev, [currentItem]: [] }));
  };

  const isItemAnswered = (idx) => {
    const item = buildSentenceItems[idx];
    const placed = answers[idx] || [];
    return placed.length === item.correctOrder.length;
  };

  const handleSubmit = () => {
    setShowResult(true);
    clearProg();
  };

  const isItemCorrect = (idx) => {
    const item = buildSentenceItems[idx];
    const placed = answers[idx] || [];
    if (placed.length !== item.correctOrder.length) return false;
    return placed.every((w, i) => w === item.correctOrder[i]);
  };

  const handleStart = () => {
    setStarted(true);
    savedData.current = null;
  };

  const handleRetry = () => {
    clearProg();
    setStarted(false);
    setCurrentItem(0);
    setAnswers({});
    setTimer(TOTAL_TIME);
    setPaused(false);
    setShowResult(false);
    setShowReview(false);
    setShowConfirm(false);
    savedData.current = null;
  };

  const score = buildSentenceItems.filter((_, i) => isItemCorrect(i)).length;

  // ─── LANDING ───
  if (!started) {
    const hasResume = !!savedData.current;
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
          <div style={{
            width: 56, height: 56, borderRadius: 16,
            background: '#00695c',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 32px',
            boxShadow: '0 4px 16px rgba(0,105,92,0.2)',
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <rect x="3" y="3" width="18" height="4" rx="1"/>
              <rect x="3" y="10" width="12" height="4" rx="1"/>
              <rect x="3" y="17" width="8" height="4" rx="1"/>
            </svg>
          </div>

          <h1 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 42, fontWeight: 400, color: '#1a1a1a',
            letterSpacing: '-0.02em', lineHeight: 1.15, marginBottom: 12,
          }}>
            Build a Sentence
          </h1>
          <p style={{
            fontSize: 15, color: '#888', lineHeight: 1.7, marginBottom: 12, fontWeight: 300,
          }}>
            10 items · 7 minutes
          </p>
          <p style={{
            fontSize: 13, color: '#aaa', lineHeight: 1.7, marginBottom: 40,
          }}>
            Arrange the word chips into a grammatically correct sentence.
            Click a chip in the word bank to place it, click a placed word to remove it.
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
    );
  }

  // ─── RESULT ───
  if (showResult && !showReview) {
    const pct = Math.round((score / TOTAL_ITEMS) * 100);
    const title = score >= 8 ? 'Excellent Work' : score >= 6 ? 'Good Effort' : 'Keep Practicing';

    return (
      <div style={{
        minHeight: '100vh', background: '#f5f5f5',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{
          textAlign: 'center', animation: 'fadeUp 0.6s ease-out',
          maxWidth: 480, padding: '40px 24px', width: '100%',
        }}>
          {/* Score ring */}
          <div style={{
            width: 120, height: 120, borderRadius: '50%',
            background: `conic-gradient(#00695c ${pct * 3.6}deg, #ddd 0deg)`,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 24px',
          }}>
            <div style={{
              width: 96, height: 96, borderRadius: '50%', background: '#f5f5f5',
              display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
            }}>
              <span style={{
                fontFamily: "'Instrument Serif', Georgia, serif",
                fontSize: 36, color: '#1a1a1a', lineHeight: 1,
              }}>{score}</span>
              <span style={{ fontSize: 11, color: '#aaa' }}>/ {TOTAL_ITEMS}</span>
            </div>
          </div>

          <h2 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 28, color: '#1a1a1a', marginBottom: 8, fontWeight: 400,
          }}>
            {title}
          </h2>
          <p style={{ fontSize: 14, color: '#888', marginBottom: 28 }}>
            {score} of {TOTAL_ITEMS} sentences correct
          </p>

          {/* Item grid */}
          <div style={{
            display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8,
            maxWidth: 300, margin: '0 auto 32px',
          }}>
            {buildSentenceItems.map((_, i) => {
              const correct = isItemCorrect(i);
              return (
                <div key={i} style={{
                  width: '100%', paddingBottom: '100%', borderRadius: 10, position: 'relative',
                  background: correct ? 'rgba(90,154,110,0.1)' : 'rgba(176,96,96,0.1)',
                  border: `1.5px solid ${correct ? 'rgba(90,154,110,0.3)' : 'rgba(176,96,96,0.3)'}`,
                }}>
                  <span style={{
                    position: 'absolute', inset: 0,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 12, fontWeight: 600,
                    color: correct ? '#5a9a6e' : '#b06060',
                  }}>{i + 1}</span>
                </div>
              );
            })}
          </div>

          <div style={{ display: 'flex', gap: 10, justifyContent: 'center', flexWrap: 'wrap' }}>
            <button
              onClick={() => setShowReview(true)}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: '#555', background: 'white',
                border: '1.5px solid #ccc', borderRadius: 10, padding: '12px 24px', cursor: 'pointer',
              }}
            >
              Review Answers
            </button>
            <button
              onClick={handleRetry}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: 'white', background: '#00695c',
                border: 'none', borderRadius: 10, padding: '12px 24px', cursor: 'pointer',
                boxShadow: '0 4px 16px rgba(0,105,92,0.2)',
              }}
            >
              Try Again
            </button>
            <button
              onClick={() => navigate('/writing')}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
                color: '#555', background: 'white',
                border: '1.5px solid #ccc', borderRadius: 10, padding: '12px 24px', cursor: 'pointer',
              }}
            >
              Back to Writing
            </button>
          </div>
        </div>
      </div>
    );
  }

  // ─── REVIEW ───
  if (showResult && showReview) {
    return (
      <div style={{
        minHeight: '100vh', background: '#f5f5f5',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ maxWidth: 720, margin: '0 auto', padding: '40px 24px' }}>
          <button
            onClick={() => setShowReview(false)}
            style={{
              fontSize: 13, fontWeight: 500, color: '#888',
              background: 'none', border: 'none', cursor: 'pointer',
              marginBottom: 32, display: 'flex', alignItems: 'center', gap: 6,
              fontFamily: "'DM Sans', sans-serif", padding: 0,
            }}
          >
            ← Back to Results
          </button>

          <h2 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 24, color: '#1a1a1a', marginBottom: 24, fontWeight: 400,
          }}>
            Answer Review
          </h2>

          {buildSentenceItems.map((item, i) => {
            const correct = isItemCorrect(i);
            const placed = answers[i] || [];

            return (
              <div key={i} style={{
                background: 'white', borderRadius: 14,
                border: `1.5px solid ${correct ? 'rgba(90,154,110,0.3)' : 'rgba(176,96,96,0.3)'}`,
                padding: 24, marginBottom: 16,
                animation: `fadeUp 0.4s ease-out ${i * 0.04}s both`,
              }}>
                {/* Header */}
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: 6, fontSize: 11, fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: correct ? 'rgba(90,154,110,0.1)' : 'rgba(176,96,96,0.1)',
                    color: correct ? '#5a9a6e' : '#b06060',
                    border: `1.5px solid ${correct ? 'rgba(90,154,110,0.3)' : 'rgba(176,96,96,0.3)'}`,
                    flexShrink: 0,
                  }}>{i + 1}</span>
                  <span style={{ fontSize: 13, color: '#555', fontStyle: 'italic' }}>
                    {item.prompt}
                  </span>
                </div>

                {/* Your answer */}
                <div style={{ marginBottom: 12 }}>
                  <p style={{ fontSize: 11, fontWeight: 600, color: '#aaa', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                    Your answer
                  </p>
                  {placed.length === 0 ? (
                    <p style={{ fontSize: 13, color: '#aaa', fontStyle: 'italic' }}>No answer given</p>
                  ) : (
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {placed.map((w, wi) => {
                        const isWordCorrect = w === item.correctOrder[wi];
                        return (
                          <span key={wi} style={{
                            fontSize: 13, fontWeight: 500, padding: '6px 12px', borderRadius: 8,
                            background: isWordCorrect ? 'rgba(90,154,110,0.08)' : 'rgba(176,96,96,0.08)',
                            border: `1.5px solid ${isWordCorrect ? 'rgba(90,154,110,0.3)' : 'rgba(176,96,96,0.3)'}`,
                            color: isWordCorrect ? '#5a9a6e' : '#b06060',
                          }}>
                            {displayWord(w)}
                          </span>
                        );
                      })}
                    </div>
                  )}
                </div>

                {/* Correct answer */}
                {!correct && (
                  <div>
                    <p style={{ fontSize: 11, fontWeight: 600, color: '#aaa', marginBottom: 8, textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                      Correct answer
                    </p>
                    <div style={{ display: 'flex', flexWrap: 'wrap', gap: 6 }}>
                      {item.correctOrder.map((w, wi) => (
                        <span key={wi} style={{
                          fontSize: 13, fontWeight: 500, padding: '6px 12px', borderRadius: 8,
                          background: 'rgba(90,154,110,0.08)',
                          border: '1.5px solid rgba(90,154,110,0.3)',
                          color: '#5a9a6e',
                        }}>
                          {displayWord(w)}
                        </span>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // ─── TEST INTERFACE ───
  const item = buildSentenceItems[currentItem];
  const placed = getCurrentPlaced();
  const slotsTotal = item.correctOrder.length;
  const slotsRemaining = slotsTotal - placed.length;
  const isAnswered = isItemAnswered(currentItem);
  const isLast = currentItem === TOTAL_ITEMS - 1;
  const answeredCount = Object.keys(answers).filter(k => isItemAnswered(Number(k))).length;

  return (
    <div style={{ minHeight: '100vh', background: '#f5f5f5', fontFamily: "'DM Sans', sans-serif" }}>

      {/* Confirm modal */}
      {showConfirm && (
        <div className="confirm-overlay" onClick={() => setShowConfirm(false)}>
          <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
            <h3>Submit Practice?</h3>
            <p>
              {answeredCount} / {TOTAL_ITEMS} completed · {formatTime(timer)} remaining
            </p>
            <div className="confirm-actions">
              <button className="btn-cancel" onClick={() => setShowConfirm(false)}>Continue</button>
              <button className="btn-confirm" onClick={() => { setShowConfirm(false); handleSubmit(); }}>Submit</button>
            </div>
          </div>
        </div>
      )}

      {/* Header */}
      <div style={{
        position: 'sticky', top: 0, zIndex: 10,
        background: 'white', borderBottom: '1px solid #ddd',
        padding: '12px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
      }}>
        {/* Timer */}
        <button
          className="timer-btn"
          onClick={() => setPaused(p => !p)}
          style={{
            color: timer < 120 ? '#b06060' : '#888',
            background: timer < 120 ? 'rgba(176,96,96,0.08)' : 'rgba(0,0,0,0.03)',
          }}
        >
          {paused ? '▶' : '⏸'} {formatTime(timer)}
          {paused && <span className="pause-badge">PAUSED</span>}
        </button>

        {/* Question nav dots */}
        <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
          {buildSentenceItems.map((_, i) => {
            const done = isItemAnswered(i);
            const isCurrent = i === currentItem;
            return (
              <button key={i} onClick={() => goToItem(i)} style={{
                width: 26, height: 26, borderRadius: 6,
                border: isCurrent ? '2px solid #00695c'
                  : done ? '1.5px solid rgba(90,154,110,0.3)'
                  : '1.5px solid #ccc',
                background: isCurrent ? 'rgba(0,105,92,0.06)'
                  : done ? 'rgba(90,154,110,0.05)' : 'white',
                fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 500,
                color: isCurrent ? '#004d40' : done ? '#5a9a6e' : '#aaa',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>
                {i + 1}
              </button>
            );
          })}
          <span style={{ fontSize: 11, color: '#aaa', marginLeft: 6 }}>
            {answeredCount}/{TOTAL_ITEMS}
          </span>
        </div>
      </div>

      {/* Main content */}
      <div style={{
        maxWidth: 720, margin: '0 auto', padding: '32px 24px 120px',
        opacity: fadeIn ? 1 : 0, transition: 'opacity 0.15s ease',
      }}>
        {/* Prompt */}
        <div style={{
          background: 'rgba(0,105,92,0.03)', borderLeft: '3px solid #00695c',
          borderRadius: '0 10px 10px 0', padding: '14px 20px', marginBottom: 28,
        }}>
          <p style={{ fontSize: 13, color: '#888', marginBottom: 4 }}>Context</p>
          <p style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 18, color: '#1a1a1a', fontWeight: 400, lineHeight: 1.5,
          }}>
            {item.prompt}
          </p>
        </div>

        {/* Answer slots */}
        <div style={{ marginBottom: 24 }}>
          <p style={{
            fontSize: 11, fontWeight: 600, color: '#aaa',
            textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12,
          }}>
            Your sentence
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 10 }}>
            {Array.from({ length: slotsTotal }).map((_, si) => {
              const word = placed[si];
              const isFilled = word !== undefined;
              return (
                <div
                  key={si}
                  className={`answer-slot ${isFilled ? 'filled' : 'empty'}`}
                  onClick={() => isFilled && handleRemoveWord(si)}
                  title={isFilled ? 'Click to remove' : ''}
                >
                  {isFilled ? displayWord(word) : ''}
                </div>
              );
            })}
          </div>
          <p style={{ fontSize: 12, color: '#aaa' }}>
            {slotsRemaining > 0
              ? `${slotsRemaining} slot${slotsRemaining !== 1 ? 's' : ''} remaining`
              : 'All slots filled'}
          </p>
        </div>

        {/* Word bank */}
        <div style={{ marginBottom: 20 }}>
          <p style={{
            fontSize: 11, fontWeight: 600, color: '#aaa',
            textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 12,
          }}>
            Word bank
          </p>
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
            {item.words.map((word, wi) => {
              const isUsed = placed.includes(word);
              return (
                <button
                  key={`${word}-${wi}`}
                  className={`word-chip ${isUsed ? 'used' : ''}`}
                  onClick={() => !isUsed && handlePlaceWord(word)}
                  disabled={isUsed}
                >
                  {displayWord(word)}
                </button>
              );
            })}
          </div>
        </div>

        {/* Reset button */}
        {placed.length > 0 && (
          <button
            onClick={handleReset}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#aaa',
              background: 'none', border: 'none', cursor: 'pointer', padding: 0,
            }}
          >
            Reset this sentence
          </button>
        )}
      </div>

      {/* Bottom nav */}
      <div style={{
        position: 'fixed', bottom: 0, left: 0, right: 0,
        background: 'white', borderTop: '1px solid #ddd',
        padding: '14px 24px', display: 'flex', justifyContent: 'space-between', alignItems: 'center',
      }}>
        <button
          onClick={() => goToItem(currentItem - 1)}
          disabled={currentItem === 0}
          style={{
            fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500,
            color: currentItem === 0 ? '#ccc' : '#555',
            background: 'none', border: 'none', cursor: currentItem === 0 ? 'default' : 'pointer',
          }}
        >
          ← Previous
        </button>

        <div className="kbd-hint">
          <span><span className="kbd">Space</span> pause</span>
          <span><span className="kbd">←</span><span className="kbd">→</span> navigate</span>
        </div>

        {isLast ? (
          <button
            onClick={() => setShowConfirm(true)}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500,
              color: 'white',
              background: '#00695c',
              border: 'none', borderRadius: 8, padding: '10px 24px', cursor: 'pointer',
            }}
          >
            Submit
          </button>
        ) : (
          <button
            onClick={() => goToItem(currentItem + 1)}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500,
              color: '#555',
              background: 'none', border: 'none', cursor: 'pointer',
            }}
          >
            Next →
          </button>
        )}
      </div>
    </div>
  );
};

export default BuildSentence;
