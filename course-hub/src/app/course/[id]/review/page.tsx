"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { SessionSummaryModal } from "@/components/SessionSummaryModal";
import { getDueCards, getExamPriorityCards, getExamDayRetrievability, interleaveByKey, loadCards, updateCard, pullCardsFromServer, Rating, type ReviewCard, getExamDate, setExamDate, isExamMode, daysUntilExam, getExamScope, setExamScope, hasExamScope, getDesiredRetention, setDesiredRetention, type DesiredRetention, getNextReviewDate } from "@/lib/spaced-repetition";
import Link from "next/link";
import { RotateCcw, Loader2, Check, Calendar, Zap, Target } from "lucide-react";
import { MistakePatterns } from "@/components/MistakePatterns";
import { TeachBackPanel } from "@/components/TeachBackPanel";
import { ReviewSparkline } from "@/components/ReviewSparkline";
import type { Question } from "@/types";
import { useI18n } from "@/lib/i18n";

export default function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { t } = useI18n();
  const [questions, setQuestions] = useState<Question[]>([]);
  const [dueCards, setDueCards] = useState<ReviewCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showRating, setShowRating] = useState(false);
  const [examActive, setExamActive] = useState(false);
  const [examDays, setExamDays] = useState<number | null>(null);
  const [showDatePicker, setShowDatePicker] = useState(false);
  const [scopeActive, setScopeActive] = useState(false);
  const [scopeKpIds, setScopeKpIds] = useState<Set<string>>(new Set());
  const [showScopeInput, setShowScopeInput] = useState(false);
  const [scopeText, setScopeText] = useState("");
  const [scopeLoading, setScopeLoading] = useState(false);
  const [scopeMatchCount, setScopeMatchCount] = useState<number | null>(null);
  const [scopeError, setScopeError] = useState<string | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [sessionAnswered, setSessionAnswered] = useState(0);
  const [sessionCorrect, setSessionCorrect] = useState(0);
  const [sessionStart] = useState(() => Date.now());
  const [sessionItems, setSessionItems] = useState<{ id: string; stem: string; correct: boolean }[]>([]);
  // Incremented after server pull completes — triggers queue recompute with fresh localStorage
  const [cardsKey, setCardsKey] = useState(0);
  const [retention, setRetention] = useState<DesiredRetention>(0.9);
  const [showRetentionPicker, setShowRetentionPicker] = useState(false);
  const [bookmarkedIds, setBookmarkedIds] = useState<Set<string>>(new Set());

  // Load questions + exam scope on mount; pull server FSRS state for cross-device sync
  useEffect(() => {
    setExamActive(isExamMode());
    setExamDays(daysUntilExam());
    setRetention(getDesiredRetention());

    const scope = getExamScope(id);
    if (scope && scope.length > 0) {
      setScopeActive(true);
      setScopeKpIds(new Set(scope));
      setScopeMatchCount(scope.length);
    }

    // Pull server card states then bump cardsKey to force queue recompute.
    // Fixes race: questions fetch may complete before pull, computing queue with stale localStorage.
    pullCardsFromServer(id).then(() => setCardsKey((k) => k + 1));

    Promise.all([
      fetch(`/api/questions?courseId=${id}`).then((r) => r.ok ? r.json() : []),
      fetch("/api/bookmarks").then((r) => r.ok ? r.json() : []),
    ]).then(([qs, bks]: [Question[], { questions?: { id?: string } }[]]) => {
      setQuestions(Array.isArray(qs) ? qs : []);
      setBookmarkedIds(new Set(
        (Array.isArray(bks) ? bks : [])
          .map((b) => b.questions?.id)
          .filter((id): id is string => Boolean(id))
      ));
      setLoading(false);
    });
  }, [id]);

  // Re-sort cards whenever questions load, exam mode, scope changes, or server pull completes
  useEffect(() => {
    if (questions.length === 0) return;

    // Filter questions by exam scope if active
    const scopedQuestions = scopeActive && scopeKpIds.size > 0
      ? questions.filter((q) => q.knowledge_point_id && scopeKpIds.has(q.knowledge_point_id))
      : questions;

    const cards = loadCards();
    const scopedQuestionIds = new Set(scopedQuestions.map((q) => q.id));
    const courseCards = cards.filter((c) => scopedQuestionIds.has(c.question_id));

    if (examActive) {
      const prioritized = getExamPriorityCards(courseCards);
      const kpMap = new Map(scopedQuestions.map((q) => [q.id, q.knowledge_point_id]));
      setDueCards(interleaveByKey(prioritized, (c) => kpMap.get(c.question_id)));
    } else {
      setDueCards(getDueCards(courseCards));
    }
    setCurrentIndex(0);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [questions, examActive, scopeActive, scopeKpIds, cardsKey]);

  function handleSetExamDate(dateStr: string) {
    if (!dateStr) {
      setExamDate(null);
      setExamActive(false);
      setExamDays(null);
    } else {
      const d = new Date(dateStr + "T23:59:59");
      setExamDate(d);
      setExamActive(true);
      setExamDays(Math.max(1, Math.ceil((d.getTime() - Date.now()) / 86400000)));
    }
    setShowDatePicker(false);
  }

  async function handleSetScope() {
    if (!scopeText.trim()) return;
    setScopeLoading(true);
    setScopeError(null);
    try {
      const res = await fetch(`/api/courses/${id}/exam-scope`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scope_text: scopeText }),
      });
      if (!res.ok) { setScopeError(t("review.scopeError")); setScopeLoading(false); return; }
      const data = await res.json();
      if (data.matched_kp_ids?.length > 0) {
        setExamScope(id, data.matched_kp_ids);
        setScopeKpIds(new Set(data.matched_kp_ids));
        setScopeActive(true);
        setScopeMatchCount(data.matched_count);
        setShowScopeInput(false);
        setScopeText("");
      } else {
        setScopeError(t("review.scopeNoMatch"));
      }
    } catch {
      setScopeError(t("review.scopeError"));
    }
    setScopeLoading(false);
  }

  function handleSetRetention(v: DesiredRetention) {
    setDesiredRetention(v);
    setRetention(v);
    setShowRetentionPicker(false);
  }

  function handleClearScope() {
    setExamScope(id, null);
    setScopeActive(false);
    setScopeKpIds(new Set());
    setScopeMatchCount(null);
  }

  function handleAnswer(questionId: string, _answer: string, isCorrect: boolean) {
    setShowRating(true);
    setSessionAnswered((n) => n + 1);
    if (isCorrect) setSessionCorrect((n) => n + 1);
    const q = questions.find((q) => q.id === questionId);
    if (q) setSessionItems((prev) => [...prev, { id: questionId, stem: q.stem, correct: isCorrect }]);
  }

  function handleOverrideCorrect(questionId: string) {
    setSessionCorrect((n) => n + 1);
    setSessionItems((prev) =>
      prev.map((item) => item.id === questionId ? { ...item, correct: true } : item)
    );
  }

  function handleRate(rating: Rating): void {
    const card = dueCards[currentIndex];
    if (card) {
      updateCard(card.question_id, rating);
    }
    setShowRating(false);
    if (currentIndex < dueCards.length - 1) {
      setCurrentIndex((i) => i + 1);
    } else {
      setDueCards([]);
      if (sessionAnswered > 0) setShowSummary(true);
    }
  }

  // Keyboard shortcut: 1=Again 2=Hard 3=Good 4=Easy (standard Anki convention)
  useEffect(() => {
    if (!showRating) return;
    function onKey(e: KeyboardEvent) {
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) return;
      const map: Record<string, Rating> = { "1": Rating.Again, "2": Rating.Hard, "3": Rating.Good, "4": Rating.Easy };
      if (map[e.key]) handleRate(map[e.key]);
    }
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [showRating]);

  const currentQuestion = dueCards[currentIndex]
    ? questions.find((q) => q.id === dueCards[currentIndex].question_id)
    : null;

  if (loading) return (
    <div>
      <CourseTabs courseId={id} />
      <Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--text-secondary)" }} />
    </div>
  );

  return (
    <div>
      <CourseTabs courseId={id} />

      {/* Exam mode banner */}
      {examActive && examDays !== null ? (
        <div className="mb-4 px-4 py-3 rounded-xl flex items-center justify-between" style={{ backgroundColor: "var(--bg-muted)" }}>
          <div className="flex items-center gap-2">
            <Zap size={16} style={{ color: "var(--warning)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--warning)" }}>
              {t("review.examModeBanner", {
                days: examDays > 1 ? t("review.examDays", { n: examDays }) : t("review.examDay", { n: examDays }),
              })}
            </span>
          </div>
          <button
            onClick={() => handleSetExamDate("")}
            className="text-xs cursor-pointer"
            style={{ color: "var(--text-muted)" }}
          >
            {t("review.turnOff")}
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowDatePicker(true)}
          className="mb-4 px-4 py-3 rounded-xl w-full text-left flex items-center gap-2 cursor-pointer transition-colors"
          style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}
        >
          <Calendar size={16} />
          <span className="text-sm">{t("review.setExamDate")}</span>
        </button>
      )}

      {showDatePicker && (
        <div className="mb-4 p-4 rounded-xl flex items-center gap-3" style={{ backgroundColor: "var(--bg-muted)" }}>
          <input
            type="date"
            min={new Date().toISOString().split("T")[0]}
            defaultValue={getExamDate()?.toISOString().split("T")[0] ?? ""}
            onChange={(e) => handleSetExamDate(e.target.value)}
            className="px-3 py-2 rounded-xl text-sm"
            style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
          />
          <button onClick={() => setShowDatePicker(false)} className="text-sm cursor-pointer" style={{ color: "var(--text-muted)" }}>
            {t("misc.cancel")}
          </button>
        </div>
      )}

      {/* Exam scope banner */}
      {scopeActive && scopeMatchCount !== null ? (
        <div className="mb-4 px-4 py-3 rounded-xl flex items-center justify-between" style={{ backgroundColor: "var(--bg-muted)" }}>
          <div className="flex items-center gap-2">
            <Target size={16} style={{ color: "var(--accent)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--accent)" }}>
              {scopeMatchCount > 1
                ? t("review.examScopeBannerPlural", { count: scopeMatchCount })
                : t("review.examScopeBanner", { count: scopeMatchCount })}
            </span>
          </div>
          <button onClick={handleClearScope} className="text-xs cursor-pointer" style={{ color: "var(--text-muted)" }}>
            {t("review.clearScope")}
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowScopeInput(true)}
          className="mb-4 px-4 py-3 rounded-xl w-full text-left flex items-center gap-2 cursor-pointer transition-colors"
          style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}
        >
          <Target size={16} />
          <span className="text-sm">{t("review.setExamScope")}</span>
        </button>
      )}

      {showScopeInput && (
        <div className="mb-4 p-4 rounded-xl space-y-3" style={{ backgroundColor: "var(--bg-muted)" }}>
          <p className="text-sm font-medium">{t("review.pasteScopeLabel")}</p>
          <textarea
            value={scopeText}
            onChange={(e) => setScopeText(e.target.value)}
            placeholder={t("review.pasteScopePlaceholder")}
            className="w-full px-3 py-2 rounded-lg text-sm"
            style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)", minHeight: "80px" }}
          />
          <div className="flex items-center gap-2">
            <button
              onClick={handleSetScope}
              disabled={scopeLoading || !scopeText.trim()}
              className="ui-button-primary disabled:opacity-30"
            >
              {scopeLoading ? <Loader2 size={14} className="animate-spin" /> : null}
              {t("review.matchKps")}
            </button>
            <button onClick={() => { setShowScopeInput(false); setScopeText(""); setScopeError(null); }} className="text-sm cursor-pointer" style={{ color: "var(--text-muted)" }}>
              {t("misc.cancel")}
            </button>
          </div>
          {scopeError && (
            <p className="text-xs" style={{ color: "var(--danger)" }}>{scopeError}</p>
          )}
        </div>
      )}

      {/* Desired retention picker */}
      <button
        onClick={() => setShowRetentionPicker((v) => !v)}
        className="mb-4 px-4 py-3 rounded-xl w-full text-left flex items-center justify-between cursor-pointer transition-colors"
        style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}
      >
        <span className="text-sm">{t("review.retentionLabel")}</span>
        <span className="text-xs font-medium" style={{ color: "var(--accent)" }}>
          {retention === 0.7 ? t("review.retention70") : retention === 0.8 ? t("review.retention80") : t("review.retention90")}
        </span>
      </button>

      {showRetentionPicker && (
        <div className="mb-4 p-4 rounded-xl space-y-3" style={{ backgroundColor: "var(--bg-muted)" }}>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("review.retentionDesc")}</p>
          <div className="grid grid-cols-3 gap-2">
            {([0.7, 0.8, 0.9] as DesiredRetention[]).map((v) => {
              const label = v === 0.7 ? t("review.retention70") : v === 0.8 ? t("review.retention80") : t("review.retention90");
              const isActive = retention === v;
              return (
                <button
                  key={v}
                  onClick={() => handleSetRetention(v)}
                  className="py-2 px-3 rounded-xl text-xs font-medium cursor-pointer transition-colors"
                  style={{
                    backgroundColor: isActive ? "var(--accent)" : "var(--bg-surface)",
                    color: isActive ? "white" : "var(--text-secondary)",
                    border: `1px solid ${isActive ? "var(--accent)" : "var(--border)"}`,
                  }}
                >
                  {label}
                </button>
              );
            })}
          </div>
        </div>
      )}

      <MistakePatterns courseId={id} />

      <div className="flex items-center gap-2 mb-6">
        <RotateCcw size={20} style={{ color: "var(--accent)" }} />
        <h2 className="text-lg font-medium">{t("review.title")}</h2>
        <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
          {dueCards.length} {t("review.due")}
        </span>
      </div>

      {dueCards.length === 0 ? (() => {
        const allCourseCards = loadCards().filter((c) => questions.some((q) => q.id === c.question_id));
        const nextDue = getNextReviewDate(allCourseCards);
        let nextDueLabel: string | null = null;
        if (nextDue) {
          const hoursUntil = (nextDue.getTime() - Date.now()) / 3_600_000;
          const daysUntil = Math.ceil(hoursUntil / 24);
          if (hoursUntil > 0 && hoursUntil < 24) {
            nextDueLabel = t("review.nextDueToday", { hours: Math.max(1, Math.round(hoursUntil)) });
          } else if (daysUntil === 1) {
            nextDueLabel = t("review.nextDueTomorrow");
          } else {
            nextDueLabel = t("review.nextDueFuture", { days: daysUntil });
          }
        }
        return (
          <div className="ui-empty rounded-[20px]">
            <Check size={32} className="mx-auto mb-3" style={{ color: "var(--success)" }} />
            <p className="font-medium mb-1">{t("review.allCaughtUp")}</p>
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {t("review.allCaughtUpDesc")}
            </p>
            {nextDueLabel && (
              <p className="text-xs mt-1 mb-4" style={{ color: "var(--accent)" }}>{nextDueLabel}</p>
            )}
            {!nextDueLabel && <div className="mb-4" />}
            <Link href={`/course/${id}/practice`} className="ui-button-secondary mb-4">
              {t("review.goPractice")}
            </Link>
            <ReviewSparkline questionIds={questions.map((q) => q.id)} />
          </div>
        );
      })() : currentQuestion ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {t("review.progress", { current: currentIndex + 1, total: dueCards.length })} {examActive ? t("review.toReview") : t("review.due")}
            </p>
            {examActive && dueCards[currentIndex] && (() => {
              const r = getExamDayRetrievability(dueCards[currentIndex]);
              return r !== null ? (
                <span className="text-xs px-2 py-1 rounded-full" style={{
                  backgroundColor: "var(--bg-muted)",
                  color: r < 0.5 ? "var(--danger)" : r < 0.8 ? "var(--warning)" : "var(--success)",
                }}>
                  {t("review.examDayRecall", { pct: Math.round(r * 100) })}
                </span>
              ) : (
                <span className="text-xs px-2 py-1 rounded-full" style={{ backgroundColor: "var(--bg-muted)", color: "var(--danger)" }}>
                  {t("review.notYetReviewed")}
                </span>
              );
            })()}
          </div>

          <QuestionCard
            key={currentQuestion.id}
            question={currentQuestion}
            onAnswer={handleAnswer}
            onOverrideCorrect={handleOverrideCorrect}
            bookmarked={bookmarkedIds.has(currentQuestion.id)}
          />

          {showRating && (
            <TeachBackPanel
              key={currentQuestion.id}
              courseId={id}
              questionId={currentQuestion.id}
            />
          )}

          {showRating && (
            <div className="mt-4 p-5 rounded-[20px]" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-sm font-medium mb-3">{t("review.howWell")}</p>
              <div className="grid grid-cols-4 gap-2">
                {([
                  { rating: Rating.Again, key: "1", label: t("review.again"), desc: t("review.againDesc"), color: "var(--danger)" },
                  { rating: Rating.Hard, key: "2", label: t("review.hard"), desc: t("review.hardDesc"), color: "var(--warning)" },
                  { rating: Rating.Good, key: "3", label: t("review.good"), desc: t("review.goodDesc"), color: "var(--success)" },
                  { rating: Rating.Easy, key: "4", label: t("review.easy"), desc: t("review.easyDesc"), color: "var(--accent)" },
                ] as { rating: Rating; key: string; label: string; desc: string; color: string }[]).map((opt) => (
                  <button
                    key={opt.rating}
                    onClick={() => handleRate(opt.rating)}
                    className="p-3 rounded-xl text-center cursor-pointer hover:opacity-80 transition-opacity relative"
                    style={{ backgroundColor: opt.color, color: "white" }}
                  >
                    <span className="absolute top-1.5 right-2 text-[9px] opacity-50">[{opt.key}]</span>
                    <p className="text-sm font-medium">{opt.label}</p>
                    <p className="text-[10px] mt-0.5 opacity-80">{opt.desc}</p>
                  </button>
                ))}
              </div>
            </div>
          )}
        </div>
      ) : null}

      <SessionSummaryModal
        open={showSummary}
        onClose={() => setShowSummary(false)}
        courseId={id}
        sessionAnswered={sessionAnswered}
        sessionCorrect={sessionCorrect}
        sessionMinutes={Math.round((Date.now() - sessionStart) / 60_000)}
        sessionStart={sessionStart}
        reviewedItems={sessionItems}
      />
    </div>
  );
}
