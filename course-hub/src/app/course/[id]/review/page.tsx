"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { getDueCards, getExamPriorityCards, getExamDayRetrievability, interleaveByKey, loadCards, updateCard, Rating, type ReviewCard, getExamDate, setExamDate, isExamMode, daysUntilExam, getExamScope, setExamScope, hasExamScope } from "@/lib/spaced-repetition";
import { RotateCcw, Loader2, Check, Calendar, Zap, Target } from "lucide-react";
import { MistakePatterns } from "@/components/MistakePatterns";
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

  // Load questions + exam scope on mount
  useEffect(() => {
    setExamActive(isExamMode());
    setExamDays(daysUntilExam());

    const scope = getExamScope(id);
    if (scope && scope.length > 0) {
      setScopeActive(true);
      setScopeKpIds(new Set(scope));
      setScopeMatchCount(scope.length);
    }

    fetch(`/api/questions?courseId=${id}`)
      .then((r) => r.json())
      .then((data: Question[]) => {
        setQuestions(data);
        setLoading(false);
      });
  }, [id]);

  // Re-sort cards whenever questions load, exam mode, or scope changes
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
  }, [questions, examActive, scopeActive, scopeKpIds]);

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

  function handleAnswer(_questionId: string, _answer: string, _isCorrect: boolean) {
    setShowRating(true);
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
        <div className="mb-4 px-4 py-3 rounded-md flex items-center justify-between" style={{ border: "1px solid var(--border)" }}>
          <div className="flex items-center gap-2">
            <Zap size={16} style={{ color: "var(--warning)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--warning)" }}>
              {`${t("review.examMode")} · ${examDays} ${t("review.daysUntilExam")} · ${t("review.weakestFirst")}`}
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
          className="mb-4 px-4 py-3 rounded-md w-full text-left flex items-center gap-2 cursor-pointer"
          style={{ border: "1px dashed var(--border)", color: "var(--text-secondary)" }}
        >
          <Calendar size={16} />
          <span className="text-sm">{t("review.setExamDate")}</span>
        </button>
      )}

      {showDatePicker && (
        <div className="mb-4 p-4 rounded-xl flex items-center gap-3" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
          <input
            type="date"
            min={new Date().toISOString().split("T")[0]}
            defaultValue={getExamDate()?.toISOString().split("T")[0] ?? ""}
            onChange={(e) => handleSetExamDate(e.target.value)}
            className="px-3 py-2 rounded-lg text-sm"
            style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}
          />
          <button onClick={() => setShowDatePicker(false)} className="text-sm cursor-pointer" style={{ color: "var(--text-muted)" }}>
            {t("review.cancel")}
          </button>
        </div>
      )}

      {/* Exam scope banner */}
      {scopeActive && scopeMatchCount !== null ? (
        <div className="mb-4 px-4 py-3 rounded-md flex items-center justify-between" style={{ border: "1px solid var(--border)" }}>
          <div className="flex items-center gap-2">
            <Target size={16} style={{ color: "var(--accent)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--accent)" }}>
              {`${t("review.examScope")} · ${scopeMatchCount} ${t("review.knowledgePoints")}`}
            </span>
          </div>
          <button onClick={handleClearScope} className="text-xs cursor-pointer" style={{ color: "var(--text-muted)" }}>
            {t("review.clearScope")}
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowScopeInput(true)}
          className="mb-4 px-4 py-3 rounded-md w-full text-left flex items-center gap-2 cursor-pointer"
          style={{ border: "1px dashed var(--border)", color: "var(--text-secondary)" }}
        >
          <Target size={16} />
          <span className="text-sm">{t("review.setScopeDesc")}</span>
        </button>
      )}

      {showScopeInput && (
        <div className="mb-4 p-4 rounded-xl space-y-3" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
          <p className="text-sm font-medium">{t("review.scopePrompt")}</p>
          <textarea
            value={scopeText}
            onChange={(e) => setScopeText(e.target.value)}
            placeholder={t("review.scopePlaceholder")}
            className="w-full px-3 py-2 rounded-lg text-sm"
            style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)", minHeight: "80px" }}
          />
          <div className="flex items-center gap-2">
            <button
              onClick={handleSetScope}
              disabled={scopeLoading || !scopeText.trim()}
              className="ui-button-primary disabled:opacity-30"
            >
              {scopeLoading ? <Loader2 size={14} className="animate-spin" /> : null}
              {t("review.matchKp")}
            </button>
            <button onClick={() => { setShowScopeInput(false); setScopeText(""); }} className="text-sm cursor-pointer" style={{ color: "var(--text-muted)" }}>
              {t("review.cancel")}
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
        <div className="text-center py-16 rounded-md" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
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
                  color: r < 0.5 ? "var(--danger)" : r < 0.8 ? "var(--warning)" : "var(--success)",
                }}>
                  {`${t("review.examDayRecall")} ${Math.round(r * 100)}%`}
                </span>
              ) : (
                <span className="text-xs px-2 py-1 rounded-full" style={{ color: "var(--danger)" }}>
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
            <div className="mt-4 p-4 rounded-md" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
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
                    className="p-3 rounded-md text-center cursor-pointer"
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
    </div>
  );
}
