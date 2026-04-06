"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { getDueCards, loadCards, updateCard, Rating, type ReviewCard, getExamDate, setExamDate, isExamMode, daysUntilExam } from "@/lib/spaced-repetition";
import { RotateCcw, Loader2, Check, Calendar, Zap } from "lucide-react";
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

  useEffect(() => {
    setExamActive(isExamMode());
    setExamDays(daysUntilExam());

    fetch(`/api/questions?courseId=${id}`)
      .then((r) => r.json())
      .then((data: Question[]) => {
        setQuestions(data);
        const cards = loadCards();
        const courseQuestionIds = new Set(data.map((q) => q.id));
        const courseCards = cards.filter((c) => courseQuestionIds.has(c.question_id));
        setDueCards(getDueCards(courseCards));
        setLoading(false);
      });
  }, [id]);

  function handleSetExamDate(dateStr: string) {
    if (!dateStr) {
      setExamDate(null);
      setExamActive(false);
      setExamDays(null);
    } else {
      setExamDate(new Date(dateStr + "T23:59:59"));
      setExamActive(true);
      setExamDays(Math.max(1, Math.ceil((new Date(dateStr + "T23:59:59").getTime() - Date.now()) / 86400000)));
    }
    setShowDatePicker(false);
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
        <div className="mb-4 px-4 py-3 rounded-xl flex items-center justify-between" style={{ backgroundColor: "rgba(245, 158, 11, 0.08)", border: "1px solid rgba(245, 158, 11, 0.3)" }}>
          <div className="flex items-center gap-2">
            <Zap size={16} style={{ color: "var(--warning)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--warning)" }}>
              {isZh ? `考试模式 · ${examDays} 天后考试` : `Exam Mode · ${examDays} day${examDays > 1 ? "s" : ""} until exam`}
            </span>
          </div>
          <button
            onClick={() => handleSetExamDate("")}
            className="text-xs cursor-pointer"
            style={{ color: "var(--text-muted)" }}
          >
            {isZh ? "关闭" : "Turn off"}
          </button>
        </div>
      ) : (
        <button
          onClick={() => setShowDatePicker(true)}
          className="mb-4 px-4 py-3 rounded-xl w-full text-left flex items-center gap-2 cursor-pointer transition-colors"
          style={{ border: "1px dashed var(--border)", color: "var(--text-secondary)" }}
        >
          <Calendar size={16} />
          <span className="text-sm">{isZh ? "设置考试日期，启用高强度复习" : "Set exam date for intensive review mode"}</span>
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
            {isZh ? "取消" : "Cancel"}
          </button>
        </div>
      )}

      <div className="flex items-center gap-2 mb-6">
        <RotateCcw size={20} style={{ color: "var(--accent)" }} />
        <h2 className="text-lg font-medium">{t("review.title")}</h2>
        <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
          {dueCards.length} {t("review.due")}
        </span>
      </div>

      {dueCards.length === 0 ? (
        <div className="text-center py-16 rounded-2xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
          <Check size={32} className="mx-auto mb-3" style={{ color: "var(--success)" }} />
          <p className="font-medium mb-1">{t("review.allCaughtUp")}</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {t("review.allCaughtUpDesc")}
          </p>
        </div>
      ) : currentQuestion ? (
        <div>
          <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>
            {currentIndex + 1} of {dueCards.length} {t("review.due")}
          </p>

          <QuestionCard
            key={currentQuestion.id}
            question={currentQuestion}
            onAnswer={handleAnswer}
          />

          {showRating && (
            <div className="mt-4 p-4 rounded-2xl" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
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
    </div>
  );
}
