import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import '../App.css';
import { passage as legacyPassage, questions as legacyQuestions, typeLabels, typeColors } from '../data.js';
import { pack6 } from '../pack6.js';
import CompleteWords from '../CompleteWords.jsx';

const STORAGE_KEY = 'toefl-reading-progress';

const loadProgress = (key) => {
  try {
    const saved = localStorage.getItem(key || STORAGE_KEY);
    if (saved) return JSON.parse(saved);
  } catch {}
  return null;
};

const saveProgress = (key, state) => {
  try {
    localStorage.setItem(key || STORAGE_KEY, JSON.stringify(state));
  } catch {}
};

const clearProgress = (key) => {
  try {
    localStorage.removeItem(key || STORAGE_KEY);
  } catch {}
};

// ═══════════════════════════════════════════
// Daily Life Reading Component
// ═══════════════════════════════════════════
const DailyLifeReading = ({ section, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResult, setShowResult] = useState(false);

  const qs = section.questions;
  const currentQ = qs[currentQuestion];
  const isCurrentAnswered = answers[currentQuestion] !== undefined;

  const handleSelect = (idx) => {
    setAnswers({ ...answers, [currentQuestion]: idx });
  };

  // Keyboard navigation
  useEffect(() => {
    if (showResult) return;
    const handler = (e) => {
      if (e.key === 'ArrowLeft' && currentQuestion > 0) {
        setCurrentQuestion(q => q - 1);
      } else if (e.key === 'ArrowRight' && isCurrentAnswered && currentQuestion < qs.length - 1) {
        setCurrentQuestion(q => q + 1);
      } else if (e.key >= '1' && e.key <= String(currentQ.options.length)) {
        handleSelect(parseInt(e.key) - 1);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showResult, currentQuestion, isCurrentAnswered]);

  const handleSubmit = () => setShowResult(true);

  const isCorrect = (qIdx) => answers[qIdx] === qs[qIdx].correct;

  const score = qs.filter((_, i) => isCorrect(i)).length;

  if (showResult) {
    return (
      <div style={{
        minHeight: '100vh', background: '#f5f5f5',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ textAlign: 'center', maxWidth: 600, padding: '0 24px', animation: 'fadeUp 0.5s ease-out' }}>
          <h2 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 28, color: '#1A1816', marginBottom: 24 }}>
            {score === qs.length ? 'Perfect!' : score >= qs.length / 2 ? 'Good Effort' : 'Keep Practicing'}
          </h2>
          <p style={{ fontSize: 14, color: '#888', marginBottom: 32 }}>{score} / {qs.length} correct</p>

          {qs.map((q, qi) => {
            const ok = isCorrect(qi);
            return (
              <div key={qi} style={{
                background: 'white', borderRadius: 14, border: '1px solid #ddd',
                padding: 24, marginBottom: 12, textAlign: 'left',
                animation: `fadeUp 0.4s ease-out ${qi * 0.05}s both`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: 6, fontSize: 11, fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: ok ? 'rgba(90,154,110,0.1)' : 'rgba(176,96,96,0.1)',
                    color: ok ? '#5a9a6e' : '#b06060',
                    border: `1.5px solid ${ok ? 'rgba(90,154,110,0.3)' : 'rgba(176,96,96,0.3)'}`,
                  }}>{ok ? '✓' : '✗'}</span>
                  <span style={{ fontSize: 13, color: '#1A1816' }}>{q.text}</span>
                </div>
                {q.options.map((opt, oi) => {
                  const isUser = answers[qi] === oi;
                  const isAnswer = q.correct === oi;
                  let bg = 'transparent', border = '#ddd', color = '#6B6560';
                  if (isAnswer) { bg = 'rgba(90,154,110,0.06)'; border = 'rgba(90,154,110,0.3)'; color = '#5a9a6e'; }
                  if (isUser && !isAnswer) { bg = 'rgba(176,96,96,0.06)'; border = 'rgba(176,96,96,0.3)'; color = '#b06060'; }
                  return (
                    <div key={oi} style={{
                      padding: '8px 12px', borderRadius: 8, marginBottom: 4,
                      border: `1.5px solid ${border}`, background: bg,
                      fontSize: 13, color, display: 'flex', alignItems: 'center', gap: 8,
                    }}>
                      {isAnswer && <span style={{ fontSize: 10 }}>✓</span>}
                      {isUser && !isAnswer && <span style={{ fontSize: 10 }}>✗</span>}
                      {!isAnswer && !isUser && <span style={{ width: 10 }}/>}
                      {opt}
                    </div>
                  );
                })}

                {q.explanation && (
                  <div style={{
                    marginTop: 8, padding: '10px 12px', borderRadius: 8,
                    background: 'rgba(0,105,92,0.04)',
                    border: '1px solid rgba(0,105,92,0.12)',
                  }}>
                    <p style={{ fontSize: 12, color: '#00695c', lineHeight: 1.7 }}>
                      <strong style={{ fontWeight: 500, color: '#004d40' }}>Explanation: </strong>
                      {q.explanation}
                    </p>
                  </div>
                )}
              </div>
            );
          })}

          {onComplete && (
            <button onClick={() => onComplete({ correct: score, total: qs.length })} style={{
              marginTop: 20, fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500,
              color: 'white', background: '#00695c',
              border: 'none', borderRadius: 10, padding: '12px 32px', cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(0,105,92,0.2)',
            }}>
              Continue
            </button>
          )}
        </div>
      </div>
    );
  }

  return (
    <div style={{
      minHeight: '100%', background: 'white',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      {/* Instruction */}
      <div style={{
        borderBottom: '3px solid #c62828',
        padding: '24px 40px 14px',
      }}>
        <h2 style={{
          fontFamily: "'Georgia', serif", fontSize: 22, fontWeight: 700,
          color: '#1a1a1a', textAlign: 'center', margin: 0,
        }}>
          Read an {section.material_type || 'email'}.
        </h2>
        <p style={{
          fontSize: 13, color: '#888', textAlign: 'center', marginTop: 6,
        }}>{section.title} — Question {currentQuestion + 1} of {qs.length}</p>
      </div>

      <div style={{
        maxWidth: 1000, margin: '0 auto', padding: '32px 40px',
        display: 'flex', gap: 32, flexWrap: 'wrap',
      }}>
        {/* Email card */}
        <div style={{
          flex: '1 1 380px', background: '#fafafa', borderRadius: 8,
          border: '2px solid #00695c', padding: 24,
        }}>
          {section.material.subject && (
            <div style={{
              display: 'flex', gap: 8, marginBottom: 16, paddingBottom: 12,
              borderBottom: '1px solid #ddd',
            }}>
              <span style={{ fontWeight: 600, fontSize: 14, color: '#555' }}>Subject:</span>
              <span style={{ fontSize: 14, color: '#1A1816' }}>{section.material.subject}</span>
            </div>
          )}
          <div style={{ fontSize: 15, lineHeight: 1.9, color: '#333', whiteSpace: 'pre-line', fontFamily: "'Georgia', serif" }}>
            {section.material.body}
          </div>
        </div>

        {/* Question */}
        <div style={{ flex: '1 1 380px' }}>
          <h3 style={{
            fontFamily: "'Georgia', serif",
            fontSize: 19, color: '#1A1816', lineHeight: 1.6,
            marginBottom: 24, fontWeight: 400,
          }}>
            {currentQ.text}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = answers[currentQuestion] === idx;
              return (
                <button key={idx} onClick={() => handleSelect(idx)} style={{
                  width: '100%', textAlign: 'left', padding: '12px 14px', borderRadius: 8,
                  border: isSelected ? '2px solid #00695c' : '1.5px solid #ccc',
                  background: isSelected ? 'rgba(0,105,92,0.04)' : 'white',
                  cursor: 'pointer', transition: 'all 0.2s ease',
                  display: 'flex', alignItems: 'center', gap: 12,
                  fontSize: 15, color: isSelected ? '#1A1816' : '#555',
                  fontFamily: "'Georgia', serif",
                }}>
                  <span style={{
                    width: 22, height: 22, borderRadius: '50%', flexShrink: 0,
                    border: isSelected ? '2px solid #00695c' : '1.5px solid #bbb',
                    background: isSelected ? '#00695c' : 'transparent',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10, fontWeight: 600, color: isSelected ? 'white' : '#bbb',
                  }}>{isSelected ? '●' : '○'}</span>
                  {opt}
                </button>
              );
            })}
          </div>

          {/* Nav — teal bar matching TOEFL style */}
          <div style={{
            marginTop: 24, padding: '10px 0',
            display: 'flex', justifyContent: 'flex-end', gap: 8,
          }}>
            <button onClick={() => setCurrentQuestion(q => q - 1)} disabled={currentQuestion === 0}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
                color: 'white', opacity: currentQuestion === 0 ? 0.4 : 1,
                background: '#00695c', border: 'none',
                borderRadius: 6, padding: '8px 20px',
                cursor: currentQuestion === 0 ? 'default' : 'pointer',
              }}>‹ Back</button>
            {currentQuestion < qs.length - 1 ? (
              <button onClick={() => setCurrentQuestion(q => q + 1)} disabled={!isCurrentAnswered}
                style={{
                  fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
                  color: '#00695c', opacity: !isCurrentAnswered ? 0.5 : 1,
                  background: '#e0f2f1', border: 'none',
                  borderRadius: 6, padding: '8px 24px',
                  cursor: !isCurrentAnswered ? 'default' : 'pointer',
                }}>Next ›</button>
            ) : (
              <button onClick={handleSubmit} disabled={!isCurrentAnswered} style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
                color: '#00695c',
                background: !isCurrentAnswered ? '#ddd' : '#e0f2f1',
                border: 'none', borderRadius: 6, padding: '8px 24px',
                cursor: !isCurrentAnswered ? 'default' : 'pointer',
              }}>Submit</button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};


// ═══════════════════════════════════════════
// Main App — Task Selector + Router
// ═══════════════════════════════════════════
const HISTORY_KEY = 'toefl-completion-history';

const loadHistory = () => {
  try { return JSON.parse(localStorage.getItem(HISTORY_KEY)) || {}; } catch { return {}; }
};
const saveHistory = (moduleId, results) => {
  try {
    const h = loadHistory();
    h[moduleId] = { results, date: new Date().toISOString() };
    localStorage.setItem(HISTORY_KEY, JSON.stringify(h));
  } catch {}
};

const Reading = () => {
  const navigate = useNavigate();
  const [view, setView] = useState('home');
  const [selectedPack, setSelectedPack] = useState(null);

  useEffect(() => { document.title = 'Reading — TOEFL Practice' }, []);
  const [selectedModule, setSelectedModule] = useState(null);
  const [currentSectionIdx, setCurrentSectionIdx] = useState(0);
  const [sectionResults, setSectionResults] = useState([]);
  const [moduleTimer, setModuleTimer] = useState(0);
  const [timerPaused, setTimerPaused] = useState(false);
  const [history, setHistory] = useState(loadHistory);

  // Module timer
  useEffect(() => {
    if (view !== 'pack' || timerPaused || moduleTimer <= 0) return;
    const interval = setInterval(() => setModuleTimer(t => t - 1), 1000);
    return () => clearInterval(interval);
  }, [view, timerPaused, moduleTimer]);

  const startLegacy = () => {
    setView('legacy');
  };

  const startPack = (pack, moduleIdx) => {
    setSelectedPack(pack);
    setSelectedModule(moduleIdx);
    setCurrentSectionIdx(0);
    setSectionResults([]);
    setModuleTimer(pack.modules[moduleIdx].time);
    setTimerPaused(false);
    setView('pack');
  };

  const handleSectionComplete = (result) => {
    const newResults = [...sectionResults, result];
    setSectionResults(newResults);

    const mod = selectedPack.modules[selectedModule];
    if (currentSectionIdx < mod.sections.length - 1) {
      setCurrentSectionIdx(currentSectionIdx + 1);
    } else {
      saveHistory(mod.id, newResults);
      setHistory(loadHistory());
      setView('pack-done');
    }
  };

  const goHome = () => {
    setView('home');
    setSelectedPack(null);
    setSelectedModule(null);
    setCurrentSectionIdx(0);
    setSectionResults([]);
  };

  // ═══ HOME ═══
  if (view === 'home') {
    const totalSets = 1 + pack6.modules.length;
    const completedSets = Object.keys(history).length;
    const totalQuestions = 10 + pack6.modules.reduce((sum, m) => sum + m.sections.reduce((s2, sec) => {
      if (sec.type === 'complete_words') return s2 + sec.paragraph.filter(p => p.blank).length;
      return s2 + (sec.questions?.length || 0);
    }, 0), 0);

    return (
      <div style={{
        fontFamily: "'DM Sans', sans-serif",
        padding: '32px 40px',
        maxWidth: 900,
      }}>
        <div style={{ marginBottom: 28 }}>
          <h1 style={{
            fontFamily: "'Georgia', serif", fontSize: 28, fontWeight: 700,
            marginBottom: 6, color: '#1a1a1a',
          }}>
            Reading Practice
          </h1>
          <p style={{ fontSize: 14, color: '#999', marginBottom: 20 }}>
            Academic passages and daily life materials
          </p>

          <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', marginBottom: 8 }}>
            {[
              { label: 'Practice Sets', value: totalSets },
              { label: 'Total Questions', value: totalQuestions },
              { label: 'Completed', value: `${completedSets} / ${totalSets}` },
              { label: 'Question Types', value: '5 types' },
            ].map((stat, i) => (
              <div key={i} style={{
                background: 'white', border: '1px solid #eee',
                borderRadius: 8, padding: '10px 16px', flex: '1 1 100px',
              }}>
                <div style={{ fontSize: 18, fontWeight: 700, color: '#00695c', marginBottom: 2 }}>{stat.value}</div>
                <div style={{ fontSize: 10, color: '#aaa', textTransform: 'uppercase', letterSpacing: '0.05em' }}>{stat.label}</div>
              </div>
            ))}
          </div>
        </div>

        <div>

          {/* Section: Standalone Passages */}
          <div style={{ marginBottom: 32 }}>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16,
            }}>
              <div style={{
                width: 4, height: 20, borderRadius: 2, background: '#00695c',
              }}/>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: '#1a1a1a', margin: 0 }}>
                Academic Passages
              </h2>
              <span style={{
                fontSize: 11, color: '#888', background: '#eee',
                padding: '2px 8px', borderRadius: 4, fontWeight: 500,
              }}>1 available</span>
            </div>

            <button onClick={startLegacy} style={{
              width: '100%', textAlign: 'left', padding: 0,
              background: 'white', borderRadius: 12,
              border: '1px solid #e0e0e0', cursor: 'pointer',
              transition: 'all 0.2s ease',
              overflow: 'hidden', display: 'flex',
              fontFamily: "'DM Sans', sans-serif",
            }}
            onMouseOver={e => { e.currentTarget.style.borderColor = '#00695c'; e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,105,92,0.1)'; }}
            onMouseOut={e => { e.currentTarget.style.borderColor = '#e0e0e0'; e.currentTarget.style.boxShadow = 'none'; }}
            >
              {/* Color accent strip */}
              <div style={{ width: 6, background: '#00695c', flexShrink: 0 }}/>
              <div style={{ padding: '20px 24px', flex: 1, display: 'flex', alignItems: 'center', gap: 16 }}>
                <div style={{
                  width: 48, height: 48, borderRadius: 10,
                  background: 'rgba(0,105,92,0.06)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  flexShrink: 0,
                }}>
                  <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#00695c" strokeWidth="1.8" strokeLinecap="round">
                    <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
                    <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
                  </svg>
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: 16, fontWeight: 600, color: '#1a1a1a', marginBottom: 4 }}>
                    Urban Agriculture
                  </div>
                  <div style={{ fontSize: 13, color: '#888', lineHeight: 1.5 }}>
                    The practice of cultivating crops within city boundaries and its impact on food security.
                  </div>
                </div>
                <div style={{ display: 'flex', gap: 8, flexShrink: 0 }}>
                  {[
                    { label: '10 Q', sub: 'questions' },
                    { label: '20m', sub: 'time limit' },
                    { label: '5', sub: 'types' },
                  ].map((t, i) => (
                    <div key={i} style={{
                      textAlign: 'center', padding: '6px 10px',
                      background: '#f8f8f8', borderRadius: 6,
                    }}>
                      <div style={{ fontSize: 14, fontWeight: 700, color: '#1a1a1a' }}>{t.label}</div>
                      <div style={{ fontSize: 9, color: '#aaa', textTransform: 'uppercase' }}>{t.sub}</div>
                    </div>
                  ))}
                </div>
                <span style={{ fontSize: 20, color: '#00695c', fontWeight: 700, marginLeft: 8 }}>›</span>
              </div>
            </button>
          </div>

          {/* Section: Pack 6 */}
          <div>
            <div style={{
              display: 'flex', alignItems: 'center', gap: 10, marginBottom: 16,
            }}>
              <div style={{
                width: 4, height: 20, borderRadius: 2, background: '#00897b',
              }}/>
              <h2 style={{ fontSize: 16, fontWeight: 700, color: '#1a1a1a', margin: 0 }}>
                Pack 6 — Mixed Practice
              </h2>
              <span style={{
                fontSize: 11, color: '#888', background: '#eee',
                padding: '2px 8px', borderRadius: 4, fontWeight: 500,
              }}>{pack6.modules.length} modules</span>
              {completedSets > 0 && (
                <span style={{
                  fontSize: 11, color: '#2e7d32', background: 'rgba(46,125,50,0.08)',
                  padding: '2px 8px', borderRadius: 4, fontWeight: 600,
                }}>{completedSets} done</span>
              )}
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
              {pack6.modules.map((mod, mi) => {
                const done = history[mod.id];
                const sectionTags = mod.sections.map(s => {
                  if (s.type === 'complete_words') return { label: 'Fill Words', color: '#e65100' };
                  if (s.type === 'daily_life') return { label: 'Email', color: '#1565c0' };
                  if (s.type === 'academic_passage') return { label: 'Passage', color: '#00695c' };
                  return { label: s.type, color: '#888' };
                });
                const qCount = mod.sections.reduce((sum, s) => {
                  if (s.type === 'complete_words') return sum + s.paragraph.filter(p => p.blank).length;
                  return sum + (s.questions?.length || 0);
                }, 0);

                return (
                  <button key={mod.id} onClick={() => startPack(pack6, mi)} style={{
                    width: '100%', textAlign: 'left', padding: 0,
                    background: done ? '#f9fffe' : 'white', borderRadius: 12,
                    border: `1px solid ${done ? 'rgba(46,125,50,0.2)' : '#e0e0e0'}`,
                    cursor: 'pointer', transition: 'all 0.2s ease',
                    overflow: 'hidden', display: 'flex',
                    fontFamily: "'DM Sans', sans-serif",
                  }}
                  onMouseOver={e => { e.currentTarget.style.borderColor = '#00695c'; e.currentTarget.style.boxShadow = '0 4px 20px rgba(0,105,92,0.1)'; }}
                  onMouseOut={e => { e.currentTarget.style.borderColor = done ? 'rgba(46,125,50,0.2)' : '#e0e0e0'; e.currentTarget.style.boxShadow = 'none'; }}
                  >
                    <div style={{ width: 6, background: done ? '#2e7d32' : '#00897b', flexShrink: 0 }}/>
                    <div style={{ padding: '16px 20px', flex: 1, display: 'flex', alignItems: 'center', gap: 14 }}>
                      {/* Module number */}
                      <div style={{
                        width: 40, height: 40, borderRadius: 10, flexShrink: 0,
                        background: done ? 'rgba(46,125,50,0.08)' : 'rgba(0,105,92,0.06)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: 15, fontWeight: 800,
                        color: done ? '#2e7d32' : '#00695c',
                      }}>{done ? '✓' : mi + 1}</div>

                      <div style={{ flex: 1 }}>
                        <div style={{
                          fontSize: 15, fontWeight: 600, color: '#1a1a1a', marginBottom: 6,
                          display: 'flex', alignItems: 'center', gap: 8,
                        }}>
                          {mod.name}
                          {done && <span style={{
                            fontSize: 10, fontWeight: 600, color: '#2e7d32',
                            background: 'rgba(46,125,50,0.08)', padding: '2px 8px', borderRadius: 4,
                          }}>COMPLETED</span>}
                        </div>
                        {/* Section tags */}
                        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' }}>
                          {sectionTags.map((tag, ti) => (
                            <span key={ti} style={{
                              fontSize: 10, fontWeight: 600, color: tag.color,
                              background: `${tag.color}11`, padding: '2px 8px', borderRadius: 4,
                              border: `1px solid ${tag.color}22`,
                            }}>{tag.label}</span>
                          ))}
                          <span style={{
                            fontSize: 10, fontWeight: 500, color: '#888',
                            padding: '2px 8px',
                          }}>
                            {qCount}Q · {Math.floor(mod.time / 60)}:{(mod.time % 60).toString().padStart(2, '0')}
                          </span>
                        </div>
                      </div>

                      <span style={{ fontSize: 20, color: '#00695c', fontWeight: 700 }}>›</span>
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Tip banner */}
          <div style={{
            marginTop: 32, padding: '16px 20px',
            background: 'rgba(0,105,92,0.04)', border: '1px solid rgba(0,105,92,0.1)',
            borderRadius: 10, display: 'flex', alignItems: 'flex-start', gap: 12,
          }}>
            <span style={{ fontSize: 18, flexShrink: 0 }}>💡</span>
            <div>
              <p style={{ fontSize: 13, fontWeight: 600, color: '#00695c', marginBottom: 4 }}>Study Tip</p>
              <p style={{ fontSize: 12, color: '#555', lineHeight: 1.6, margin: 0 }}>
                Start with the academic passage to build vocabulary, then move to Pack 6 for mixed practice.
                Each module includes fill-in-the-blank, email reading, and passage comprehension.
              </p>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ═══ LEGACY MODE ═══
  if (view === 'legacy') {
    return <LegacyReadingTest onBack={goHome} />;
  }

  // ═══ PACK MODE — render current section ═══
  if (view === 'pack') {
    const mod = selectedPack.modules[selectedModule];
    const section = mod.sections[currentSectionIdx];

    const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

    // Compute question range for display
    const getQuestionRange = () => {
      let start = 1;
      for (let i = 0; i < currentSectionIdx; i++) {
        const s = mod.sections[i];
        if (s.type === 'complete_words') start += s.paragraph.filter(p => p.blank).length;
        else if (s.questions) start += s.questions.length;
      }
      const cur = mod.sections[currentSectionIdx];
      const count = cur.type === 'complete_words' ? cur.paragraph.filter(p => p.blank).length : (cur.questions?.length || 0);
      const total = mod.sections.reduce((sum, s) => {
        if (s.type === 'complete_words') return sum + s.paragraph.filter(p => p.blank).length;
        return sum + (s.questions?.length || 0);
      }, 0);
      return `Questions ${start}–${start + count - 1} of ${total}`;
    };

    const tealBtn = (label, icon, onClick) => (
      <button onClick={onClick} style={{
        fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
        color: 'white', background: 'rgba(255,255,255,0.12)',
        border: '1px solid rgba(255,255,255,0.25)', borderRadius: 6,
        padding: '7px 18px', cursor: 'pointer',
        display: 'flex', alignItems: 'center', gap: 6,
        transition: 'background 0.15s ease',
      }}
      onMouseOver={e => e.currentTarget.style.background = 'rgba(255,255,255,0.22)'}
      onMouseOut={e => e.currentTarget.style.background = 'rgba(255,255,255,0.12)'}
      >
        {label} {icon && <span style={{ fontSize: 11 }}>{icon}</span>}
      </button>
    );

    const isLast = currentSectionIdx === mod.sections.length - 1;

    const sectionHeader = (
      <div style={{ position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50 }}>
        {/* Single light bar */}
        <div style={{
          background: 'white',
          padding: '8px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          fontFamily: "'DM Sans', sans-serif", fontSize: 13,
          borderBottom: '2px solid #00695c',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
            <button onClick={goHome} style={{
              fontSize: 12, color: '#888', background: 'transparent',
              border: '1px solid #ddd', borderRadius: 5, padding: '4px 12px', cursor: 'pointer',
              fontFamily: 'inherit', fontWeight: 500,
            }}>← Home</button>
            <span style={{ fontWeight: 700, color: '#00695c' }}>Reading</span>
            <span style={{ color: '#ccc' }}>|</span>
            <span style={{ color: '#888' }}>{getQuestionRange()}</span>
            <div style={{ display: 'flex', gap: 3, marginLeft: 8 }}>
              {mod.sections.map((_, i) => (
                <div key={i} style={{
                  width: 20, height: 3, borderRadius: 2,
                  background: i < currentSectionIdx ? '#2e7d32'
                    : i === currentSectionIdx ? '#00695c' : '#ddd',
                }} />
              ))}
            </div>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <span style={{
              fontSize: 14, fontWeight: 600, fontVariantNumeric: 'tabular-nums',
              color: moduleTimer < 60 ? '#c62828' : '#1a1a1a',
            }}>
              {formatTime(moduleTimer)}
            </span>
            <span style={{
              fontSize: 12, color: '#aaa', cursor: 'pointer',
            }} onClick={() => setTimerPaused(p => !p)}>
              {timerPaused ? '▶ Resume' : '⏸ Hide Time'}
            </span>
            <button onClick={() => {
              if (isLast) return;
              handleSectionComplete({ correct: 0, total: 0 });
            }} style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
              color: 'white', background: '#00695c',
              border: 'none', borderRadius: 6,
              padding: '6px 18px', cursor: 'pointer',
            }}>
              Next ›
            </button>
          </div>
        </div>
      </div>
    );

    return (
      <div style={{ paddingTop: 48 }}>
        {sectionHeader}

        {section.type === 'complete_words' && (
          <CompleteWords
            section={section}
            onComplete={handleSectionComplete}
          />
        )}

        {section.type === 'daily_life' && (
          <DailyLifeReading
            section={section}
            onComplete={handleSectionComplete}
          />
        )}

        {section.type === 'academic_passage' && (
          <AcademicPassage
            section={section}
            onComplete={handleSectionComplete}
          />
        )}
      </div>
    );
  }

  // ═══ PACK DONE ═══
  if (view === 'pack-done') {
    const mod = selectedPack.modules[selectedModule];
    return (
      <div style={{
        minHeight: '100vh', background: '#f5f5f5',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ textAlign: 'center', maxWidth: 480, padding: '0 24px', animation: 'fadeUp 0.6s ease-out' }}>
          <h2 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 28, color: '#1A1816', marginBottom: 24,
          }}>
            {mod.name} Complete
          </h2>

          {mod.sections.map((sec, i) => (
            <div key={i} style={{
              background: 'white', borderRadius: 10, border: '1px solid #ddd',
              padding: '14px 20px', marginBottom: 8, textAlign: 'left',
              display: 'flex', justifyContent: 'space-between', alignItems: 'center',
            }}>
              <span style={{ fontSize: 13, color: '#4A4640' }}>
                {sec.title || sec.type}
              </span>
              <span style={{ fontSize: 13, fontWeight: 500, color: '#5a9a6e' }}>
                {sectionResults[i]?.correct ?? '—'} / {sectionResults[i]?.total ?? '—'}
              </span>
            </div>
          ))}

          <button onClick={goHome} style={{
            marginTop: 24, fontSize: 14, fontWeight: 500, color: 'white',
            background: '#00695c',
            border: 'none', borderRadius: 10, padding: '12px 32px', cursor: 'pointer',
            boxShadow: '0 4px 16px rgba(0,105,92,0.2)',
            fontFamily: "'DM Sans', sans-serif",
          }}>
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  return null;
};


// ═══════════════════════════════════════════
// Academic Passage Component (reusable)
// ═══════════════════════════════════════════
const AcademicPassage = ({ section, onComplete }) => {
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResult, setShowResult] = useState(false);
  const [fadeIn, setFadeIn] = useState(true);
  const passageRef = useRef(null);
  const paragraphRefs = useRef([]);

  const qs = section.questions;
  const paragraphs = section.passage.split('\n\n');
  const currentQ = qs[currentQuestion];

  useEffect(() => {
    setFadeIn(false);
    const t = setTimeout(() => setFadeIn(true), 50);
    return () => clearTimeout(t);
  }, [currentQuestion]);

  const isCurrentAnswered = answers[currentQuestion] !== undefined;

  // Keyboard navigation
  useEffect(() => {
    if (showResult) return;
    const handler = (e) => {
      if (e.key === 'ArrowLeft' && currentQuestion > 0) {
        setCurrentQuestion(q => q - 1);
      } else if (e.key === 'ArrowRight' && isCurrentAnswered && currentQuestion < qs.length - 1) {
        setCurrentQuestion(q => q + 1);
      } else if (e.key >= '1' && e.key <= String(currentQ.options.length)) {
        handleSelect(parseInt(e.key) - 1);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [showResult, currentQuestion, isCurrentAnswered]);

  const handleSelect = (idx) => {
    setAnswers({ ...answers, [currentQuestion]: idx });
  };

  const handleSubmit = () => {
    setShowResult(true);
    if (onComplete) {
      const correct = qs.filter((q, i) => answers[i] === q.correct).length;
      onComplete({ correct, total: qs.length });
    }
  };

  const isCorrect = (qIdx) => answers[qIdx] === qs[qIdx].correct;

  // Review after submit
  if (showResult) {
    const correct = qs.filter((_, i) => isCorrect(i)).length;
    return (
      <div style={{
        minHeight: '100vh', background: '#f5f5f5', fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ maxWidth: 720, margin: '0 auto', padding: '48px 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <h2 style={{
              fontFamily: "'Instrument Serif', Georgia, serif",
              fontSize: 28, color: '#1A1816', marginBottom: 8,
            }}>
              {section.title}
            </h2>
            <p style={{ fontSize: 14, color: '#888' }}>{correct} / {qs.length} correct</p>
          </div>

          {qs.map((q, qi) => {
            const ok = isCorrect(qi);
            const tc = typeColors[q.question_type] || typeColors.detail;
            return (
              <div key={qi} style={{
                background: 'white', borderRadius: 14, border: '1px solid #ddd',
                padding: 24, marginBottom: 12,
                animation: `fadeUp 0.4s ease-out ${qi * 0.05}s both`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: 6, fontSize: 11, fontWeight: 600,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: ok ? 'rgba(90,154,110,0.1)' : 'rgba(176,96,96,0.1)',
                    color: ok ? '#5a9a6e' : '#b06060',
                    border: `1.5px solid ${ok ? 'rgba(90,154,110,0.3)' : 'rgba(176,96,96,0.3)'}`,
                  }}>{qi + 1}</span>
                  {q.question_type && tc && (
                    <span style={{
                      fontSize: 10, fontWeight: 500, color: tc.text, background: tc.bg,
                      border: `1px solid ${tc.border}`, padding: '2px 8px', borderRadius: 5,
                    }}>{typeLabels[q.question_type] || q.question_type}</span>
                  )}
                  <span style={{
                    marginLeft: 'auto', fontSize: 11, fontWeight: 500,
                    color: ok ? '#5a9a6e' : '#b06060',
                  }}>{ok ? '✓' : '✗'}</span>
                </div>
                <p style={{ fontSize: 13, color: '#1A1816', lineHeight: 1.6, marginBottom: 12 }}>{q.text}</p>
                {q.options.map((opt, oi) => {
                  const isUser = answers[qi] === oi;
                  const isAnswer = q.correct === oi;
                  let bg = 'transparent', border = '#ddd', color = '#6B6560';
                  if (isAnswer) { bg = 'rgba(90,154,110,0.06)'; border = 'rgba(90,154,110,0.3)'; color = '#5a9a6e'; }
                  if (isUser && !isAnswer) { bg = 'rgba(176,96,96,0.06)'; border = 'rgba(176,96,96,0.3)'; color = '#b06060'; }
                  return (
                    <div key={oi} style={{
                      padding: '8px 12px', borderRadius: 8, marginBottom: 4,
                      border: `1.5px solid ${border}`, background: bg,
                      fontSize: 12, color, display: 'flex', alignItems: 'center', gap: 8,
                    }}>
                      {isAnswer && <span style={{ fontSize: 10 }}>✓</span>}
                      {isUser && !isAnswer && <span style={{ fontSize: 10 }}>✗</span>}
                      {!isAnswer && !isUser && <span style={{ width: 10 }}/>}
                      {opt}
                    </div>
                  );
                })}

                {q.explanation && (
                  <div style={{
                    marginTop: 8, padding: '12px 14px', borderRadius: 8,
                    background: 'rgba(0,105,92,0.04)',
                    border: '1px solid rgba(0,105,92,0.12)',
                  }}>
                    <p style={{ fontSize: 12, color: '#00695c', lineHeight: 1.7 }}>
                      <strong style={{ fontWeight: 500, color: '#004d40' }}>Explanation: </strong>
                      {q.explanation}
                    </p>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  }

  // Auto-scroll to relevant paragraph
  useEffect(() => {
    const pIdx = currentQ?.paragraph;
    if (pIdx != null && paragraphRefs.current[pIdx] && passageRef.current) {
      const el = paragraphRefs.current[pIdx];
      const container = passageRef.current;
      container.scrollTo({ top: el.offsetTop - container.offsetTop - 20, behavior: 'smooth' });
    }
  }, [currentQuestion]);

  // Render passage text with highlighted word
  const renderParagraph = (para, idx) => {
    const hw = currentQ?.highlighted_word;
    if (hw && currentQ?.paragraph === idx && para.includes(hw)) {
      const parts = para.split(hw);
      return (
        <>
          <span style={{ fontSize: 10, fontWeight: 600, color: '#C4B5A0', marginRight: 6 }}>P{idx + 1}</span>
          {parts[0]}
          <span style={{
            background: 'rgba(82,130,175,0.15)', padding: '1px 3px', borderRadius: 3,
            borderBottom: '2px solid #4a7fa5', fontWeight: 500,
          }}>{hw}</span>
          {parts.slice(1).join(hw)}
        </>
      );
    }
    return (
      <>
        <span style={{ fontSize: 10, fontWeight: 600, color: '#C4B5A0', marginRight: 6 }}>P{idx + 1}</span>
        {para}
      </>
    );
  };

  // Test interface
  return (
    <div className="test-layout" style={{
      display: 'flex', height: 'calc(100vh - 48px)', background: 'white',
      fontFamily: "'Georgia', serif",
    }}>
      {/* Passage */}
      <div className="passage-panel" style={{
        width: '50%', display: 'flex', flexDirection: 'column',
        borderRight: '1px solid #ddd', background: 'white',
      }}>
        <div style={{
          padding: '14px 24px', borderBottom: '1px solid #ddd',
          fontFamily: "'DM Sans', sans-serif",
        }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#1A1816' }}>{section.title}</h2>
        </div>
        <div ref={passageRef} className="passage-content" style={{
          flex: 1, overflowY: 'auto', padding: '24px 28px',
        }}>
          {paragraphs.map((para, idx) => (
            <p key={idx} ref={el => paragraphRefs.current[idx] = el} style={{
              fontFamily: "'Georgia', serif", fontSize: 16, lineHeight: 2.0,
              color: '#333', marginBottom: 20, fontWeight: 400,
              padding: '8px 12px', borderRadius: 4,
              borderLeft: currentQ?.paragraph === idx ? '3px solid #00695c' : '3px solid transparent',
              background: currentQ?.paragraph === idx ? 'rgba(0,105,92,0.03)' : 'transparent',
              transition: 'all 0.4s ease',
            }}>
              {renderParagraph(para, idx)}
            </p>
          ))}
        </div>
      </div>

      {/* Questions */}
      <div className="question-panel" style={{
        width: '50%', display: 'flex', flexDirection: 'column', background: '#f5f5f5',
      }}>
        {/* Nav dots */}
        <div style={{
          padding: '12px 24px', borderBottom: '1px solid #ddd',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', gap: 4 }}>
            {qs.map((_, i) => (
              <button key={i} onClick={() => setCurrentQuestion(i)} style={{
                width: 26, height: 26, borderRadius: 6,
                border: i === currentQuestion ? '2px solid #D4A574'
                  : answers[i] !== undefined ? '1.5px solid rgba(90,154,110,0.3)'
                  : '1.5px solid #ccc',
                background: i === currentQuestion ? 'rgba(212,165,116,0.08)'
                  : answers[i] !== undefined ? 'rgba(90,154,110,0.05)' : 'white',
                fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 500,
                color: i === currentQuestion ? '#C4956A' : answers[i] !== undefined ? '#5a9a6e' : '#aaa',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>{i + 1}</button>
            ))}
          </div>
          <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#aaa' }}>
            {Object.keys(answers).length} / {qs.length}
          </span>
        </div>

        {/* Question */}
        <div className="question-content" style={{
          flex: 1, overflowY: 'auto', padding: '28px 28px 20px',
          opacity: fadeIn ? 1 : 0, transition: 'opacity 0.15s ease',
        }}>
          {currentQ.question_type && typeColors[currentQ.question_type] && (
            <div style={{
              display: 'inline-flex', padding: '3px 10px', borderRadius: 5, marginBottom: 16,
              background: typeColors[currentQ.question_type].bg,
              border: `1px solid ${typeColors[currentQ.question_type].border}`,
            }}>
              <span style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 500,
                color: typeColors[currentQ.question_type].text,
              }}>{typeLabels[currentQ.question_type] || currentQ.question_type}</span>
            </div>
          )}

          <h3 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 18, color: '#1A1816', lineHeight: 1.5,
            marginBottom: 24, fontWeight: 400,
          }}>{currentQ.text}</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = answers[currentQuestion] === idx;
              return (
                <button key={idx} onClick={() => handleSelect(idx)} style={{
                  width: '100%', textAlign: 'left', padding: '12px 14px', borderRadius: 8,
                  border: isSelected ? '2px solid #00695c' : '1.5px solid #ccc',
                  background: isSelected ? 'rgba(0,105,92,0.04)' : 'white',
                  cursor: 'pointer', transition: 'all 0.2s ease',
                  display: 'flex', alignItems: 'center', gap: 10,
                  fontFamily: "'DM Sans', sans-serif", fontSize: 14,
                  color: isSelected ? '#1A1816' : '#555',
                }}>
                  <span style={{
                    width: 22, height: 22, borderRadius: '50%', flexShrink: 0,
                    border: isSelected ? '2px solid #00695c' : '1.5px solid #bbb',
                    background: isSelected ? '#00695c' : 'transparent',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10, fontWeight: 600, color: isSelected ? 'white' : '#bbb',
                  }}>{String.fromCharCode(65 + idx)}</span>
                  {opt}
                </button>
              );
            })}
          </div>
        </div>

        {/* Nav — TOEFL teal bar */}
        <div style={{
          padding: '10px 20px', background: '#00695c',
          display: 'flex', justifyContent: 'flex-end', gap: 8,
        }}>
          <button onClick={() => setCurrentQuestion(q => q - 1)} disabled={currentQuestion === 0}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
              color: 'white', opacity: currentQuestion === 0 ? 0.4 : 1,
              background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)',
              borderRadius: 6, padding: '8px 20px',
              cursor: currentQuestion === 0 ? 'default' : 'pointer',
            }}>‹ Back</button>
          {currentQuestion < qs.length - 1 ? (
            <button onClick={() => setCurrentQuestion(q => q + 1)} disabled={!isCurrentAnswered}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
                color: '#00695c', opacity: !isCurrentAnswered ? 0.5 : 1,
                background: 'white', border: 'none',
                borderRadius: 6, padding: '8px 24px',
                cursor: !isCurrentAnswered ? 'default' : 'pointer',
              }}>Next ›</button>
          ) : (
            <button onClick={handleSubmit} disabled={!isCurrentAnswered} style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600,
              color: '#00695c',
              background: !isCurrentAnswered ? 'rgba(255,255,255,0.4)' : 'white',
              border: 'none', borderRadius: 6, padding: '8px 24px',
              cursor: !isCurrentAnswered ? 'default' : 'pointer',
            }}>Submit</button>
          )}
        </div>
      </div>
    </div>
  );
};


// ═══════════════════════════════════════════
// Legacy Reading Test (original component)
// ═══════════════════════════════════════════
const LegacyReadingTest = ({ onBack }) => {
  const TOTAL_TIME = 20 * 60;
  const saved = useRef(loadProgress(STORAGE_KEY));
  const questions = legacyQuestions;
  const paragraphs = legacyPassage.split('\n\n');

  const [currentQuestion, setCurrentQuestion] = useState(saved.current?.currentQuestion || 0);
  const [answers, setAnswers] = useState(saved.current?.answers || {});
  const [selectedMultiple, setSelectedMultiple] = useState([]);
  const [showResult, setShowResult] = useState(false);
  const [showReview, setShowReview] = useState(false);
  const [timer, setTimer] = useState(saved.current?.timer || TOTAL_TIME);
  const [paused, setPaused] = useState(false);
  const [fadeIn, setFadeIn] = useState(true);
  const [showConfirm, setShowConfirm] = useState(false);
  const passageRef = useRef(null);
  const paragraphRefs = useRef([]);

  useEffect(() => {
    if (!showResult && !paused && timer > 0) {
      const interval = setInterval(() => setTimer(t => t - 1), 1000);
      return () => clearInterval(interval);
    }
    if (timer === 0 && !showResult) { setShowResult(true); clearProgress(STORAGE_KEY); }
  }, [showResult, paused, timer]);

  useEffect(() => {
    if (!showResult) saveProgress(STORAGE_KEY, { currentQuestion, answers, timer });
  }, [currentQuestion, answers, timer, showResult]);

  useEffect(() => {
    setFadeIn(false);
    const t = setTimeout(() => setFadeIn(true), 50);
    return () => clearTimeout(t);
  }, [currentQuestion, showResult, showReview]);

  useEffect(() => {
    const pIdx = questions[currentQuestion]?.paragraph;
    if (pIdx != null && paragraphRefs.current[pIdx] && passageRef.current) {
      const el = paragraphRefs.current[pIdx];
      const container = passageRef.current;
      container.scrollTo({ top: el.offsetTop - container.offsetTop - 20, behavior: 'smooth' });
    }
  }, [currentQuestion]);

  const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

  const handleSelectAnswer = (idx) => {
    if (questions[currentQuestion].type === 'multiple') {
      setSelectedMultiple(prev => {
        if (prev.includes(idx)) return prev.filter(i => i !== idx);
        if (prev.length < 3) return [...prev, idx];
        return prev;
      });
    } else {
      setAnswers({ ...answers, [currentQuestion]: idx });
    }
  };

  const handleNext = () => {
    if (questions[currentQuestion].type === 'multiple') setAnswers(a => ({ ...a, [currentQuestion]: selectedMultiple }));
    if (currentQuestion < questions.length - 1) { setCurrentQuestion(currentQuestion + 1); setSelectedMultiple([]); }
  };

  const handlePrev = () => {
    if (currentQuestion > 0) {
      if (questions[currentQuestion].type === 'multiple' && selectedMultiple.length > 0)
        setAnswers(a => ({ ...a, [currentQuestion]: selectedMultiple }));
      setCurrentQuestion(currentQuestion - 1);
      const prevA = answers[currentQuestion - 1];
      setSelectedMultiple(questions[currentQuestion - 1].type === 'multiple' && Array.isArray(prevA) ? prevA : []);
    }
  };

  const handleSubmit = () => {
    if (questions[currentQuestion].type === 'multiple') setAnswers(a => ({ ...a, [currentQuestion]: selectedMultiple }));
    setShowResult(true); clearProgress(STORAGE_KEY);
  };

  const handleRetry = () => {
    setCurrentQuestion(0); setAnswers({}); setSelectedMultiple([]);
    setShowResult(false); setShowReview(false); setTimer(TOTAL_TIME);
    setPaused(false); setShowConfirm(false); clearProgress(STORAGE_KEY);
  };

  const isCurrentAnswered = () => {
    if (questions[currentQuestion].type === 'multiple') return selectedMultiple.length === 3;
    return answers[currentQuestion] !== undefined;
  };

  const isCorrect = (qIdx) => {
    const q = questions[qIdx];
    if (q.type === 'multiple') {
      const ua = answers[qIdx] || [];
      return Array.isArray(ua) && JSON.stringify([...ua].sort()) === JSON.stringify([...q.correct].sort());
    }
    return answers[qIdx] === q.correct;
  };

  const calculateScore = () => {
    let correct = 0;
    for (let i = 0; i < questions.length; i++) {
      if (isCorrect(i)) correct++;
    }
    return { correct, total: questions.length, scaled: Math.round((correct / questions.length) * 30) };
  };

  const currentQ = questions[currentQuestion];
  const tc = typeColors[currentQ.type];

  // Results
  if (showResult && !showReview) {
    const { correct, total, scaled } = calculateScore();
    const pct = Math.round((correct / total) * 100);
    return (
      <div style={{ minHeight: '100vh', background: '#f5f5f5', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Georgia', serif" }}>
        <div style={{ textAlign: 'center', animation: 'fadeUp 0.6s ease-out', maxWidth: 480, padding: '0 24px' }}>
          <div style={{ width: 120, height: 120, borderRadius: '50%', background: `conic-gradient(#D4A574 ${pct * 3.6}deg, #ddd 0deg)`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 28px' }}>
            <div style={{ width: 100, height: 100, borderRadius: '50%', background: '#f5f5f5', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 36, color: '#1A1816' }}>{scaled}</span>
              <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#aaa' }}>/ 30</span>
            </div>
          </div>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#888', marginBottom: 28 }}>{correct} / {total} correct</p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button onClick={() => setShowReview(true)} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: '#6B6560', background: 'white', border: '1.5px solid #ccc', borderRadius: 10, padding: '12px 28px', cursor: 'pointer' }}>Review</button>
            <button onClick={handleRetry} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: 'white', background: '#00695c', border: 'none', borderRadius: 10, padding: '12px 28px', cursor: 'pointer' }}>Retry</button>
            <button onClick={onBack} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: '#6B6560', background: 'white', border: '1.5px solid #ccc', borderRadius: 10, padding: '12px 28px', cursor: 'pointer' }}>Home</button>
          </div>
        </div>
      </div>
    );
  }

  // Main test (simplified — key parts preserved)
  return (
    <div className="test-layout" style={{ display: 'flex', height: '100vh', background: '#f5f5f5', fontFamily: "'Georgia', serif" }}>
      {showConfirm && (
        <div className="confirm-overlay" onClick={() => setShowConfirm(false)}>
          <div className="confirm-dialog" onClick={e => e.stopPropagation()}>
            <h3>Submit Test?</h3>
            <p>{Object.keys(answers).length} / {questions.length} answered · {formatTime(timer)} remaining</p>
            <div className="confirm-actions">
              <button className="btn-cancel" onClick={() => setShowConfirm(false)}>Continue</button>
              <button className="btn-confirm" onClick={() => { setShowConfirm(false); handleSubmit(); }}>Submit</button>
            </div>
          </div>
        </div>
      )}

      <div className="passage-panel" style={{ width: '50%', display: 'flex', flexDirection: 'column', borderRight: '1px solid #ddd', background: 'white' }}>
        <div style={{ padding: '18px 28px', borderBottom: '1px solid #ddd', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button onClick={onBack} style={{ fontSize: 12, color: '#888', background: 'none', border: '1px solid #ccc', borderRadius: 6, padding: '4px 12px', cursor: 'pointer', fontFamily: "'DM Sans', sans-serif" }}>← Home</button>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600, color: '#1A1816' }}>Urban Agriculture</span>
          </div>
          <button className="timer-btn" onClick={() => setPaused(p => !p)} style={{ color: timer < 120 ? '#b06060' : '#888', background: timer < 120 ? 'rgba(176,96,96,0.08)' : 'rgba(0,0,0,0.03)' }}>
            {paused ? '▶' : '⏸'} {formatTime(timer)}
            {paused && <span className="pause-badge">PAUSED</span>}
          </button>
        </div>
        <div ref={passageRef} className="passage-content" style={{ flex: 1, overflowY: 'auto', padding: '28px 32px' }}>
          {paragraphs.map((para, idx) => (
            <p key={idx} ref={el => paragraphRefs.current[idx] = el} style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.85, color: '#4A4640',
              marginBottom: 20, fontWeight: 300, padding: '8px 12px', borderRadius: 8,
              borderLeft: currentQ.paragraph === idx ? '2.5px solid #D4A574' : '2.5px solid transparent',
              background: currentQ.paragraph === idx ? 'rgba(212,165,116,0.04)' : 'transparent',
              transition: 'all 0.4s ease',
            }}>
              <span style={{ fontSize: 10, fontWeight: 600, color: '#C4B5A0', marginRight: 6 }}>P{idx + 1}</span>
              {para}
            </p>
          ))}
        </div>
      </div>

      <div className="question-panel" style={{ width: '50%', display: 'flex', flexDirection: 'column', background: '#f5f5f5' }}>
        <div style={{ padding: '16px 28px', borderBottom: '1px solid #ddd', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: 6 }}>
            {questions.map((_, i) => (
              <button key={i} onClick={() => { setCurrentQuestion(i); setSelectedMultiple(questions[i].type === 'multiple' && Array.isArray(answers[i]) ? answers[i] : []); }} style={{
                width: 26, height: 26, borderRadius: 6,
                border: i === currentQuestion ? '2px solid #D4A574' : answers[i] !== undefined ? '1.5px solid rgba(90,154,110,0.3)' : '1.5px solid #ccc',
                background: i === currentQuestion ? 'rgba(212,165,116,0.08)' : answers[i] !== undefined ? 'rgba(90,154,110,0.05)' : 'white',
                fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 500,
                color: i === currentQuestion ? '#C4956A' : answers[i] !== undefined ? '#5a9a6e' : '#aaa',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>{i + 1}</button>
            ))}
          </div>
        </div>

        <div className="question-content" style={{ flex: 1, overflowY: 'auto', padding: '32px 32px 24px', opacity: fadeIn ? 1 : 0, transition: 'opacity 0.15s ease' }}>
          <div style={{ display: 'inline-flex', padding: '4px 12px', borderRadius: 6, marginBottom: 20, background: tc.bg, border: `1px solid ${tc.border}` }}>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 500, color: tc.text }}>{typeLabels[currentQ.type]}</span>
          </div>
          <h3 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 20, color: '#1A1816', lineHeight: 1.5, marginBottom: 28, fontWeight: 400 }}>{currentQ.text}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = currentQ.type === 'multiple' ? selectedMultiple.includes(idx) : answers[currentQuestion] === idx;
              return (
                <button key={idx} onClick={() => handleSelectAnswer(idx)} style={{
                  width: '100%', textAlign: 'left', padding: '14px 16px', borderRadius: 10,
                  border: isSelected ? '1.5px solid #D4A574' : '1.5px solid #ccc',
                  background: isSelected ? 'rgba(0,105,92,0.04)' : 'white',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12,
                }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: 7, flexShrink: 0,
                    border: isSelected ? '2px solid #D4A574' : '1.5px solid #D4CFC5',
                    background: isSelected ? '#D4A574' : 'transparent',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 600,
                    color: isSelected ? 'white' : '#aaa',
                  }}>{String.fromCharCode(65 + idx)}</span>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: isSelected ? '#1A1816' : '#6B6560' }}>{opt}</span>
                </button>
              );
            })}
          </div>
          {currentQ.type === 'multiple' && selectedMultiple.length > 0 && (
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#aaa', marginTop: 16 }}>{selectedMultiple.length} of 3 selected</p>
          )}
        </div>

        <div style={{ padding: '16px 28px', borderTop: '1px solid #ddd', background: 'white', display: 'flex', justifyContent: 'space-between' }}>
          <button onClick={handlePrev} disabled={currentQuestion === 0} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500, color: currentQuestion === 0 ? '#D4CFC5' : '#6B6560', background: 'none', border: 'none', cursor: currentQuestion === 0 ? 'default' : 'pointer' }}>← Previous</button>
          {currentQuestion < questions.length - 1 ? (
            <button onClick={handleNext} disabled={!isCurrentAnswered()} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500, color: !isCurrentAnswered() ? '#D4CFC5' : '#6B6560', background: 'none', border: 'none', cursor: !isCurrentAnswered() ? 'default' : 'pointer' }}>Next →</button>
          ) : (
            <button onClick={() => setShowConfirm(true)} disabled={!isCurrentAnswered()} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500, color: 'white', background: !isCurrentAnswered() ? '#D4CFC5' : 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)', border: 'none', borderRadius: 8, padding: '10px 24px', cursor: !isCurrentAnswered() ? 'default' : 'pointer' }}>Submit</button>
          )}
        </div>
      </div>
    </div>
  );
};

export default Reading;
