import React, { useState, useEffect, useRef, useCallback } from 'react';
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

  const handleSubmit = () => setShowResult(true);

  const isCorrect = (qIdx) => answers[qIdx] === qs[qIdx].correct;

  const score = qs.filter((_, i) => isCorrect(i)).length;

  if (showResult) {
    return (
      <div style={{
        minHeight: '100vh', background: '#FAFAF8',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ textAlign: 'center', maxWidth: 600, padding: '0 24px', animation: 'fadeUp 0.5s ease-out' }}>
          <h2 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 28, color: '#2D2A26', marginBottom: 24 }}>
            {score === qs.length ? 'Perfect!' : score >= qs.length / 2 ? 'Good Effort' : 'Keep Practicing'}
          </h2>
          <p style={{ fontSize: 14, color: '#8A8477', marginBottom: 32 }}>{score} / {qs.length} correct</p>

          {qs.map((q, qi) => {
            const ok = isCorrect(qi);
            return (
              <div key={qi} style={{
                background: 'white', borderRadius: 14, border: '1px solid #EDE8E0',
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
                  <span style={{ fontSize: 13, color: '#2D2A26' }}>{q.text}</span>
                </div>
                {q.options.map((opt, oi) => {
                  const isUser = answers[qi] === oi;
                  const isAnswer = q.correct === oi;
                  let bg = 'transparent', border = '#EDE8E0', color = '#6B6560';
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
                    background: 'rgba(212,165,116,0.06)',
                    border: '1px solid rgba(212,165,116,0.15)',
                  }}>
                    <p style={{ fontSize: 12, color: '#8A7A65', lineHeight: 1.7 }}>
                      <strong style={{ fontWeight: 500, color: '#6B5D4D' }}>Explanation: </strong>
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
              color: 'white', background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
              border: 'none', borderRadius: 10, padding: '12px 32px', cursor: 'pointer',
              boxShadow: '0 4px 16px rgba(212,165,116,0.25)',
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
      minHeight: '100vh', background: '#FAFAF8',
      fontFamily: "'DM Sans', sans-serif",
    }}>
      {/* Header */}
      <div style={{
        padding: '18px 28px', borderBottom: '1px solid #EDE8E0', background: 'white',
        display: 'flex', alignItems: 'center', gap: 12,
      }}>
        <div style={{
          width: 32, height: 32, borderRadius: 9,
          background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
          display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="2" strokeLinecap="round">
            <rect x="2" y="3" width="20" height="18" rx="2"/><path d="M2 8h20"/>
          </svg>
        </div>
        <div>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#2D2A26' }}>Read an {section.material_type || 'email'}.</h2>
          <p style={{ fontSize: 11, color: '#ADA899', marginTop: 1 }}>{section.title}</p>
        </div>
        <span style={{ marginLeft: 'auto', fontSize: 11, color: '#ADA899' }}>
          Question {currentQuestion + 1} of {qs.length}
        </span>
      </div>

      <div style={{
        maxWidth: 960, margin: '0 auto', padding: '32px 24px',
        display: 'flex', gap: 32, flexWrap: 'wrap',
      }}>
        {/* Email card */}
        <div style={{
          flex: '1 1 360px', background: 'white', borderRadius: 14,
          border: '2px solid #D4A574', padding: 24,
        }}>
          {section.material.subject && (
            <div style={{
              display: 'flex', gap: 8, marginBottom: 16, paddingBottom: 12,
              borderBottom: '1px solid #EDE8E0',
            }}>
              <span style={{ fontWeight: 600, fontSize: 13, color: '#6B6560' }}>Subject:</span>
              <span style={{ fontSize: 13, color: '#2D2A26' }}>{section.material.subject}</span>
            </div>
          )}
          <div style={{ fontSize: 14, lineHeight: 1.8, color: '#4A4640', whiteSpace: 'pre-line' }}>
            {section.material.body}
          </div>
        </div>

        {/* Question */}
        <div style={{ flex: '1 1 360px' }}>
          <h3 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 18, color: '#2D2A26', lineHeight: 1.5,
            marginBottom: 24, fontWeight: 400,
          }}>
            {currentQ.text}
          </h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = answers[currentQuestion] === idx;
              return (
                <button key={idx} onClick={() => handleSelect(idx)} style={{
                  width: '100%', textAlign: 'left', padding: '14px 16px', borderRadius: 10,
                  border: isSelected ? '1.5px solid #D4A574' : '1.5px solid #E2DDD5',
                  background: isSelected ? 'rgba(212,165,116,0.06)' : 'white',
                  cursor: 'pointer', transition: 'all 0.2s ease',
                  display: 'flex', alignItems: 'center', gap: 12, fontSize: 14, color: isSelected ? '#2D2A26' : '#6B6560',
                }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: 6, flexShrink: 0,
                    border: isSelected ? '2px solid #D4A574' : '1.5px solid #D4CFC5',
                    background: isSelected ? '#D4A574' : 'transparent',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 11, fontWeight: 600, color: isSelected ? 'white' : '#ADA899',
                  }}>○</span>
                  {opt}
                </button>
              );
            })}
          </div>

          <div style={{ marginTop: 24, display: 'flex', justifyContent: 'space-between' }}>
            <button onClick={() => setCurrentQuestion(q => q - 1)} disabled={currentQuestion === 0}
              style={{
                fontSize: 13, fontWeight: 500, color: currentQuestion === 0 ? '#D4CFC5' : '#6B6560',
                background: 'none', border: 'none', cursor: currentQuestion === 0 ? 'default' : 'pointer',
                fontFamily: "'DM Sans', sans-serif",
              }}>← Back</button>

            {currentQuestion < qs.length - 1 ? (
              <button onClick={() => setCurrentQuestion(q => q + 1)} disabled={!isCurrentAnswered}
                style={{
                  fontSize: 13, fontWeight: 500, color: !isCurrentAnswered ? '#D4CFC5' : '#6B6560',
                  background: 'none', border: 'none', cursor: !isCurrentAnswered ? 'default' : 'pointer',
                  fontFamily: "'DM Sans', sans-serif",
                }}>Next →</button>
            ) : (
              <button onClick={handleSubmit} disabled={!isCurrentAnswered} style={{
                fontSize: 13, fontWeight: 500, color: 'white',
                background: !isCurrentAnswered ? '#D4CFC5' : 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
                border: 'none', borderRadius: 8, padding: '10px 24px',
                cursor: !isCurrentAnswered ? 'default' : 'pointer',
                fontFamily: "'DM Sans', sans-serif",
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
  const [view, setView] = useState('home');
  const [selectedPack, setSelectedPack] = useState(null);
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
    return (
      <div style={{
        minHeight: '100vh', background: '#FAFAF8',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'Georgia', serif",
      }}>
        <div style={{
          textAlign: 'center', animation: 'fadeUp 0.8s ease-out',
          maxWidth: 640, padding: '0 24px',
        }}>
          <div style={{
            width: 56, height: 56, borderRadius: 16,
            background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            margin: '0 auto 32px',
            boxShadow: '0 4px 16px rgba(212,165,116,0.3)',
          }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
              <path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"/>
              <path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"/>
              <line x1="8" y1="7" x2="16" y2="7"/><line x1="8" y1="11" x2="14" y2="11"/>
            </svg>
          </div>

          <h1 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 42, fontWeight: 400, color: '#2D2A26',
            letterSpacing: '-0.02em', lineHeight: 1.15, marginBottom: 12,
          }}>
            TOEFL Reading
          </h1>
          <p style={{
            fontFamily: "'DM Sans', sans-serif",
            fontSize: 15, color: '#8A8477', lineHeight: 1.7, marginBottom: 40, fontWeight: 300,
          }}>
            Select a practice set to begin
          </p>

          <div style={{
            display: 'flex', flexDirection: 'column', gap: 12, maxWidth: 480, margin: '0 auto',
          }}>
            {/* Legacy passage */}
            <button onClick={startLegacy} style={{
              width: '100%', textAlign: 'left', padding: '20px 24px',
              background: 'white', borderRadius: 14,
              border: '1.5px solid #E2DDD5', cursor: 'pointer',
              transition: 'all 0.2s ease',
              display: 'flex', alignItems: 'center', gap: 16,
              fontFamily: "'DM Sans', sans-serif",
            }}
            onMouseOver={e => e.currentTarget.style.borderColor = '#D4A574'}
            onMouseOut={e => e.currentTarget.style.borderColor = '#E2DDD5'}
            >
              <div style={{
                width: 40, height: 40, borderRadius: 10,
                background: 'rgba(130,100,170,0.08)', border: '1px solid rgba(130,100,170,0.2)',
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: 18, flexShrink: 0,
              }}>📖</div>
              <div>
                <div style={{ fontSize: 15, fontWeight: 500, color: '#2D2A26', marginBottom: 4 }}>
                  Urban Agriculture
                </div>
                <div style={{ fontSize: 12, color: '#ADA899' }}>
                  Academic passage · 10 questions · 20 min
                </div>
              </div>
              <span style={{ marginLeft: 'auto', fontSize: 18, color: '#D4CFC5' }}>→</span>
            </button>

            {/* Pack 6 modules */}
            {pack6.modules.map((mod, mi) => {
              const sectionSummary = mod.sections.map(s => {
                if (s.type === 'complete_words') return 'Fill Words';
                if (s.type === 'daily_life') return `Email (${s.questions.length}Q)`;
                if (s.type === 'academic_passage') return `Passage (${s.questions.length}Q)`;
                return s.type;
              }).join(' + ');

              const done = history[mod.id];

              return (
                <button key={mod.id} onClick={() => startPack(pack6, mi)} style={{
                  width: '100%', textAlign: 'left', padding: '20px 24px',
                  background: 'white', borderRadius: 14,
                  border: '1.5px solid #E2DDD5', cursor: 'pointer',
                  transition: 'all 0.2s ease',
                  display: 'flex', alignItems: 'center', gap: 16,
                  fontFamily: "'DM Sans', sans-serif",
                }}
                onMouseOver={e => e.currentTarget.style.borderColor = '#D4A574'}
                onMouseOut={e => e.currentTarget.style.borderColor = '#E2DDD5'}
                >
                  <div style={{
                    width: 40, height: 40, borderRadius: 10,
                    background: 'rgba(82,130,175,0.08)', border: '1px solid rgba(82,130,175,0.2)',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 14, fontWeight: 600, color: '#4a7fa5', flexShrink: 0,
                  }}>P6</div>
                  <div>
                    <div style={{ fontSize: 15, fontWeight: 500, color: '#2D2A26', marginBottom: 4 }}>
                      Pack 6 — {mod.name}
                      {done && <span style={{
                        marginLeft: 8, fontSize: 10, fontWeight: 600, color: '#5a9a6e',
                        background: 'rgba(90,154,110,0.1)', padding: '2px 8px', borderRadius: 4,
                      }}>DONE</span>}
                    </div>
                    <div style={{ fontSize: 12, color: '#ADA899' }}>
                      {sectionSummary} · {Math.floor(mod.time / 60)}:{(mod.time % 60).toString().padStart(2, '0')}
                    </div>
                  </div>
                  <span style={{ marginLeft: 'auto', fontSize: 18, color: done ? '#5a9a6e' : '#D4CFC5' }}>{done ? '✓' : '→'}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    );
  }

  // ═══ LEGACY MODE (original reading test) ═══
  if (view === 'legacy') {
    return <LegacyReadingTest onBack={goHome} />;
  }

  // ═══ PACK MODE — render current section ═══
  if (view === 'pack') {
    const mod = selectedPack.modules[selectedModule];
    const section = mod.sections[currentSectionIdx];

    const formatTime = (s) => `${Math.floor(s / 60)}:${(s % 60).toString().padStart(2, '0')}`;

    const sectionHeader = (
      <div style={{
        position: 'fixed', top: 0, left: 0, right: 0, zIndex: 50,
        background: 'white', borderBottom: '1px solid #EDE8E0',
        padding: '8px 20px', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <button onClick={goHome} style={{
          fontSize: 12, color: '#8A8477', background: 'none', border: '1px solid #E2DDD5',
          borderRadius: 6, padding: '4px 12px', cursor: 'pointer', fontFamily: 'inherit',
        }}>← Home</button>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ display: 'flex', gap: 4 }}>
            {mod.sections.map((_, i) => (
              <div key={i} style={{
                width: 20, height: 4, borderRadius: 2,
                background: i < currentSectionIdx ? '#5a9a6e'
                  : i === currentSectionIdx ? '#D4A574' : '#E2DDD5',
                transition: 'background 0.3s',
              }} />
            ))}
          </div>
          <span style={{ fontSize: 11, color: '#ADA899' }}>
            {currentSectionIdx + 1}/{mod.sections.length}
          </span>
        </div>

        <button onClick={() => setTimerPaused(p => !p)} className="timer-btn" style={{
          color: moduleTimer < 60 ? '#b06060' : '#8A8477',
          background: moduleTimer < 60 ? 'rgba(176,96,96,0.08)' : 'rgba(0,0,0,0.03)',
          fontSize: 12, padding: '4px 10px',
        }}>
          {timerPaused ? '▶' : '⏸'} {formatTime(moduleTimer)}
          {timerPaused && <span className="pause-badge">PAUSED</span>}
        </button>
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
        minHeight: '100vh', background: '#FAFAF8',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ textAlign: 'center', maxWidth: 480, padding: '0 24px', animation: 'fadeUp 0.6s ease-out' }}>
          <h2 style={{
            fontFamily: "'Instrument Serif', Georgia, serif",
            fontSize: 28, color: '#2D2A26', marginBottom: 24,
          }}>
            {mod.name} Complete
          </h2>

          {mod.sections.map((sec, i) => (
            <div key={i} style={{
              background: 'white', borderRadius: 10, border: '1px solid #EDE8E0',
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
            background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
            border: 'none', borderRadius: 10, padding: '12px 32px', cursor: 'pointer',
            boxShadow: '0 4px 16px rgba(212,165,116,0.25)',
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
        minHeight: '100vh', background: '#FAFAF8', fontFamily: "'DM Sans', sans-serif",
      }}>
        <div style={{ maxWidth: 720, margin: '0 auto', padding: '48px 24px' }}>
          <div style={{ textAlign: 'center', marginBottom: 32 }}>
            <h2 style={{
              fontFamily: "'Instrument Serif', Georgia, serif",
              fontSize: 28, color: '#2D2A26', marginBottom: 8,
            }}>
              {section.title}
            </h2>
            <p style={{ fontSize: 14, color: '#8A8477' }}>{correct} / {qs.length} correct</p>
          </div>

          {qs.map((q, qi) => {
            const ok = isCorrect(qi);
            const tc = typeColors[q.question_type] || typeColors.detail;
            return (
              <div key={qi} style={{
                background: 'white', borderRadius: 14, border: '1px solid #EDE8E0',
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
                <p style={{ fontSize: 13, color: '#2D2A26', lineHeight: 1.6, marginBottom: 12 }}>{q.text}</p>
                {q.options.map((opt, oi) => {
                  const isUser = answers[qi] === oi;
                  const isAnswer = q.correct === oi;
                  let bg = 'transparent', border = '#EDE8E0', color = '#6B6560';
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
                    background: 'rgba(212,165,116,0.06)',
                    border: '1px solid rgba(212,165,116,0.15)',
                  }}>
                    <p style={{ fontSize: 12, color: '#8A7A65', lineHeight: 1.7 }}>
                      <strong style={{ fontWeight: 500, color: '#6B5D4D' }}>Explanation: </strong>
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
      display: 'flex', height: 'calc(100vh - 48px)', background: '#FAFAF8',
      fontFamily: "'Georgia', serif",
    }}>
      {/* Passage */}
      <div className="passage-panel" style={{
        width: '50%', display: 'flex', flexDirection: 'column',
        borderRight: '1px solid #EDE8E0', background: 'white',
      }}>
        <div style={{
          padding: '14px 24px', borderBottom: '1px solid #EDE8E0',
          fontFamily: "'DM Sans', sans-serif",
        }}>
          <h2 style={{ fontSize: 13, fontWeight: 600, color: '#2D2A26' }}>{section.title}</h2>
        </div>
        <div ref={passageRef} className="passage-content" style={{
          flex: 1, overflowY: 'auto', padding: '24px 28px',
        }}>
          {paragraphs.map((para, idx) => (
            <p key={idx} ref={el => paragraphRefs.current[idx] = el} style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 14, lineHeight: 1.85,
              color: '#4A4640', marginBottom: 20, fontWeight: 300,
              padding: '8px 12px', borderRadius: 8,
              borderLeft: currentQ?.paragraph === idx ? '2.5px solid #D4A574' : '2.5px solid transparent',
              background: currentQ?.paragraph === idx ? 'rgba(212,165,116,0.04)' : 'transparent',
              transition: 'all 0.4s ease',
            }}>
              {renderParagraph(para, idx)}
            </p>
          ))}
        </div>
      </div>

      {/* Questions */}
      <div className="question-panel" style={{
        width: '50%', display: 'flex', flexDirection: 'column', background: '#FAFAF8',
      }}>
        {/* Nav dots */}
        <div style={{
          padding: '12px 24px', borderBottom: '1px solid #EDE8E0',
          display: 'flex', alignItems: 'center', justifyContent: 'space-between',
        }}>
          <div style={{ display: 'flex', gap: 4 }}>
            {qs.map((_, i) => (
              <button key={i} onClick={() => setCurrentQuestion(i)} style={{
                width: 26, height: 26, borderRadius: 6,
                border: i === currentQuestion ? '2px solid #D4A574'
                  : answers[i] !== undefined ? '1.5px solid rgba(90,154,110,0.3)'
                  : '1.5px solid #E2DDD5',
                background: i === currentQuestion ? 'rgba(212,165,116,0.08)'
                  : answers[i] !== undefined ? 'rgba(90,154,110,0.05)' : 'white',
                fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 500,
                color: i === currentQuestion ? '#C4956A' : answers[i] !== undefined ? '#5a9a6e' : '#ADA899',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>{i + 1}</button>
            ))}
          </div>
          <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#ADA899' }}>
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
            fontSize: 18, color: '#2D2A26', lineHeight: 1.5,
            marginBottom: 24, fontWeight: 400,
          }}>{currentQ.text}</h3>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = answers[currentQuestion] === idx;
              return (
                <button key={idx} onClick={() => handleSelect(idx)} style={{
                  width: '100%', textAlign: 'left', padding: '12px 14px', borderRadius: 10,
                  border: isSelected ? '1.5px solid #D4A574' : '1.5px solid #E2DDD5',
                  background: isSelected ? 'rgba(212,165,116,0.06)' : 'white',
                  cursor: 'pointer', transition: 'all 0.2s ease',
                  display: 'flex', alignItems: 'center', gap: 10,
                  fontFamily: "'DM Sans', sans-serif", fontSize: 13,
                  color: isSelected ? '#2D2A26' : '#6B6560',
                }}>
                  <span style={{
                    width: 22, height: 22, borderRadius: 6, flexShrink: 0,
                    border: isSelected ? '2px solid #D4A574' : '1.5px solid #D4CFC5',
                    background: isSelected ? '#D4A574' : 'transparent',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 10, fontWeight: 600, color: isSelected ? 'white' : '#ADA899',
                  }}>{String.fromCharCode(65 + idx)}</span>
                  {opt}
                </button>
              );
            })}
          </div>
        </div>

        {/* Nav */}
        <div style={{
          padding: '14px 24px', borderTop: '1px solid #EDE8E0', background: 'white',
          display: 'flex', justifyContent: 'space-between',
        }}>
          <button onClick={() => setCurrentQuestion(q => q - 1)} disabled={currentQuestion === 0}
            style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500,
              color: currentQuestion === 0 ? '#D4CFC5' : '#6B6560',
              background: 'none', border: 'none', cursor: currentQuestion === 0 ? 'default' : 'pointer',
            }}>← Previous</button>
          {currentQuestion < qs.length - 1 ? (
            <button onClick={() => setCurrentQuestion(q => q + 1)} disabled={!isCurrentAnswered}
              style={{
                fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500,
                color: !isCurrentAnswered ? '#D4CFC5' : '#6B6560',
                background: 'none', border: 'none', cursor: !isCurrentAnswered ? 'default' : 'pointer',
              }}>Next →</button>
          ) : (
            <button onClick={handleSubmit} disabled={!isCurrentAnswered} style={{
              fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 500, color: 'white',
              background: !isCurrentAnswered ? '#D4CFC5' : 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)',
              border: 'none', borderRadius: 8, padding: '10px 24px',
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
      <div style={{ minHeight: '100vh', background: '#FAFAF8', display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: "'Georgia', serif" }}>
        <div style={{ textAlign: 'center', animation: 'fadeUp 0.6s ease-out', maxWidth: 480, padding: '0 24px' }}>
          <div style={{ width: 120, height: 120, borderRadius: '50%', background: `conic-gradient(#D4A574 ${pct * 3.6}deg, #EDE8E0 0deg)`, display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 28px' }}>
            <div style={{ width: 100, height: 100, borderRadius: '50%', background: '#FAFAF8', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center' }}>
              <span style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 36, color: '#2D2A26' }}>{scaled}</span>
              <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, color: '#ADA899' }}>/ 30</span>
            </div>
          </div>
          <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: '#8A8477', marginBottom: 28 }}>{correct} / {total} correct</p>
          <div style={{ display: 'flex', gap: 12, justifyContent: 'center' }}>
            <button onClick={() => setShowReview(true)} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: '#6B6560', background: 'white', border: '1.5px solid #E2DDD5', borderRadius: 10, padding: '12px 28px', cursor: 'pointer' }}>Review</button>
            <button onClick={handleRetry} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: 'white', background: 'linear-gradient(135deg, #D4A574 0%, #C4956A 100%)', border: 'none', borderRadius: 10, padding: '12px 28px', cursor: 'pointer' }}>Retry</button>
            <button onClick={onBack} style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, fontWeight: 500, color: '#6B6560', background: 'white', border: '1.5px solid #E2DDD5', borderRadius: 10, padding: '12px 28px', cursor: 'pointer' }}>Home</button>
          </div>
        </div>
      </div>
    );
  }

  // Main test (simplified — key parts preserved)
  return (
    <div className="test-layout" style={{ display: 'flex', height: '100vh', background: '#FAFAF8', fontFamily: "'Georgia', serif" }}>
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

      <div className="passage-panel" style={{ width: '50%', display: 'flex', flexDirection: 'column', borderRight: '1px solid #EDE8E0', background: 'white' }}>
        <div style={{ padding: '18px 28px', borderBottom: '1px solid #EDE8E0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <button onClick={onBack} style={{ fontSize: 12, color: '#8A8477', background: 'none', border: '1px solid #E2DDD5', borderRadius: 6, padding: '4px 12px', cursor: 'pointer', fontFamily: "'DM Sans', sans-serif" }}>← Home</button>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 13, fontWeight: 600, color: '#2D2A26' }}>Urban Agriculture</span>
          </div>
          <button className="timer-btn" onClick={() => setPaused(p => !p)} style={{ color: timer < 120 ? '#b06060' : '#8A8477', background: timer < 120 ? 'rgba(176,96,96,0.08)' : 'rgba(0,0,0,0.03)' }}>
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

      <div className="question-panel" style={{ width: '50%', display: 'flex', flexDirection: 'column', background: '#FAFAF8' }}>
        <div style={{ padding: '16px 28px', borderBottom: '1px solid #EDE8E0', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', gap: 6 }}>
            {questions.map((_, i) => (
              <button key={i} onClick={() => { setCurrentQuestion(i); setSelectedMultiple(questions[i].type === 'multiple' && Array.isArray(answers[i]) ? answers[i] : []); }} style={{
                width: 26, height: 26, borderRadius: 6,
                border: i === currentQuestion ? '2px solid #D4A574' : answers[i] !== undefined ? '1.5px solid rgba(90,154,110,0.3)' : '1.5px solid #E2DDD5',
                background: i === currentQuestion ? 'rgba(212,165,116,0.08)' : answers[i] !== undefined ? 'rgba(90,154,110,0.05)' : 'white',
                fontFamily: "'DM Sans', sans-serif", fontSize: 10, fontWeight: 500,
                color: i === currentQuestion ? '#C4956A' : answers[i] !== undefined ? '#5a9a6e' : '#ADA899',
                cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
              }}>{i + 1}</button>
            ))}
          </div>
        </div>

        <div className="question-content" style={{ flex: 1, overflowY: 'auto', padding: '32px 32px 24px', opacity: fadeIn ? 1 : 0, transition: 'opacity 0.15s ease' }}>
          <div style={{ display: 'inline-flex', padding: '4px 12px', borderRadius: 6, marginBottom: 20, background: tc.bg, border: `1px solid ${tc.border}` }}>
            <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 500, color: tc.text }}>{typeLabels[currentQ.type]}</span>
          </div>
          <h3 style={{ fontFamily: "'Instrument Serif', Georgia, serif", fontSize: 20, color: '#2D2A26', lineHeight: 1.5, marginBottom: 28, fontWeight: 400 }}>{currentQ.text}</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {currentQ.options.map((opt, idx) => {
              const isSelected = currentQ.type === 'multiple' ? selectedMultiple.includes(idx) : answers[currentQuestion] === idx;
              return (
                <button key={idx} onClick={() => handleSelectAnswer(idx)} style={{
                  width: '100%', textAlign: 'left', padding: '14px 16px', borderRadius: 10,
                  border: isSelected ? '1.5px solid #D4A574' : '1.5px solid #E2DDD5',
                  background: isSelected ? 'rgba(212,165,116,0.06)' : 'white',
                  cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 12,
                }}>
                  <span style={{
                    width: 24, height: 24, borderRadius: 7, flexShrink: 0,
                    border: isSelected ? '2px solid #D4A574' : '1.5px solid #D4CFC5',
                    background: isSelected ? '#D4A574' : 'transparent',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontFamily: "'DM Sans', sans-serif", fontSize: 11, fontWeight: 600,
                    color: isSelected ? 'white' : '#ADA899',
                  }}>{String.fromCharCode(65 + idx)}</span>
                  <span style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 14, color: isSelected ? '#2D2A26' : '#6B6560' }}>{opt}</span>
                </button>
              );
            })}
          </div>
          {currentQ.type === 'multiple' && selectedMultiple.length > 0 && (
            <p style={{ fontFamily: "'DM Sans', sans-serif", fontSize: 12, color: '#ADA899', marginTop: 16 }}>{selectedMultiple.length} of 3 selected</p>
          )}
        </div>

        <div style={{ padding: '16px 28px', borderTop: '1px solid #EDE8E0', background: 'white', display: 'flex', justifyContent: 'space-between' }}>
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
