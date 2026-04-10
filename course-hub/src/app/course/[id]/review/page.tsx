"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { SessionSummaryModal } from "@/components/SessionSummaryModal";
import { getDueCards, getExamPriorityCards, getExamDayRetrievability, interleaveByKey, loadCards, updateCard, pullCardsFromServer, Rating, type ReviewCard, getExamDate, setExamDate, isExamMode, daysUntilExam, getExamScope, setExamScope, hasExamScope } from "@/lib/spaced-repetition";
import { RotateCcw, Loader2, Check, Calendar, Zap, Target } from "lucide-react";
import { MistakePatterns } from "@/components/MistakePatterns";
import { TeachBackPanel } from "@/components/TeachBackPanel";
import type { Question } from "@/types";
import { useI18n } from "@/lib/i18n";

export default function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { t, locale } = useI18n();
  const isZh = locale === "zh";
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
  const [showSummary, setShowSummary] = useState(false);
  const [sessionAnswered, setSessionAnswered] = useState(0);
  const [sessionCorrect, setSessionCorrect] = useState(0);
  const [sessionStart] = useState(() => Date.now());
  const [sessionItems, setSessionItems] = useState<{ id: string; stem: string; correct: boolean }[]>([]);
  // Incremented after server pull completes — triggers queue recompute with fresh localStorage
  const [cardsKey, setCardsKey] = useState(0);

  // Load questions + exam scope on mount; pull server FSRS state for cross-device sync
  useEffect(() => {
    setExamActive(isExamMode());
    setExamDays(daysUntilExam());

    const scope = getExamScope(id);
    if (scope && scope.length > 0) {
      setScopeActive(true);
      setScopeKpIds(new Set(scope));
      setScopeMatchCount(scope.length);
    }

    // Pull server card states then bump cardsKey to force queue recompute.
    // Fixes race: questions fetch may complete before pull, computing queue with stale localStorage.
    pullCardsFromServer(id).then(() => setCardsKey((k) => k + 1));

    fetch(`/api/questions?courseId=${id}`)
      .then((r) => r.ok ? r.json() : [])
      .then((data: Question[]) => {
        setQuestions(Array.isArray(data) ? data : []);
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
    try {
      const res = await fetch(`/api/courses/${id}/exam-scope`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ scope_text: scopeText }),
      });
      const data = await res.json();
      if (data.matched_kp_ids?.length > 0) {
        setExamScope(id, data.matched_kp_ids);
        setScopeKpIds(new Set(data.matched_kp_ids));
        setScopeActive(true);
        setScopeMatchCount(data.matched_count);
        setShowScopeInput(false);
        setScopeText("");
      }
    } catch { /* ignore */ }
    setScopeLoading(false);
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
              {isZh
                ? `考试模式 · ${examDays} 天后考试 · 按薄弱程度排序`
                : `Exam Mode · ${examDays} day${examDays > 1 ? "s" : ""} · weakest first`}
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
              {isZh
                ? `考试范围 · ${scopeMatchCount} 个知识点`
                : `Exam Scope · ${scopeMatchCount} knowledge point${scopeMatchCount > 1 ? "s" : ""}`}
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
            <button onClick={() => { setShowScopeInput(false); setScopeText(""); }} className="text-sm cursor-pointer" style={{ color: "var(--text-muted)" }}>
              {t("misc.cancel")}
            </button>
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

      {dueCards.length === 0 ? (
        <div className="ui-empty rounded-[20px]">
          <Check size={32} className="mx-auto mb-3" style={{ color: "var(--success)" }} />
          <p className="font-medium mb-1">{t("review.allCaughtUp")}</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {t("review.allCaughtUpDesc")}
          </p>
        </div>
      ) : currentQuestion ? (
        <div>
          <div className="flex items-center justify-between mb-3">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {currentIndex + 1} of {dueCards.length} {examActive ? t("review.toReview") : t("review.due")}
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
                  { rating: Rating.Again, label: t("review.again"), desc: t("review.againDesc"), color: "var(--danger)" },
                  { rating: Rating.Hard, label: t("review.hard"), desc: t("review.hardDesc"), color: "var(--warning)" },
                  { rating: Rating.Good, label: t("review.good"), desc: t("review.goodDesc"), color: "var(--success)" },
                  { rating: Rating.Easy, label: t("review.easy"), desc: t("review.easyDesc"), color: "var(--accent)" },
                ] as { rating: Rating; label: string; desc: string; color: string }[]).map((opt) => (
                  <button
                    key={opt.rating}
                    onClick={() => handleRate(opt.rating)}
                    className="p-3 rounded-xl text-center cursor-pointer hover:opacity-80 transition-opacity"
                    style={{ backgroundColor: opt.color, color: "white" }}
                  >
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
