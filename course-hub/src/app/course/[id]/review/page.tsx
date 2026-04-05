"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { getDueCards, loadCards, updateCard, Rating, type ReviewCard } from "@/lib/spaced-repetition";
import { RotateCcw, Loader2, Check } from "lucide-react";
import type { Question } from "@/types";

export default function ReviewPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [dueCards, setDueCards] = useState<ReviewCard[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [showRating, setShowRating] = useState(false);

  useEffect(() => {
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

      <div className="flex items-center gap-2 mb-6">
        <RotateCcw size={20} style={{ color: "var(--accent)" }} />
        <h2 className="text-lg font-medium">Spaced Review</h2>
        <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
          {dueCards.length} due
        </span>
      </div>

      {dueCards.length === 0 ? (
        <div className="text-center py-16 rounded-2xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
          <Check size={32} className="mx-auto mb-3" style={{ color: "var(--success)" }} />
          <p className="font-medium mb-1">All caught up</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            No questions due for review right now. Keep practicing to build your review queue.
          </p>
        </div>
      ) : currentQuestion ? (
        <div>
          <p className="text-sm mb-3" style={{ color: "var(--text-secondary)" }}>
            {currentIndex + 1} of {dueCards.length} due
          </p>

          <QuestionCard
            key={currentQuestion.id}
            question={currentQuestion}
            onAnswer={handleAnswer}
          />

          {showRating && (
            <div className="mt-4 p-4 rounded-2xl" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
              <p className="text-sm font-medium mb-3">How well did you know this?</p>
              <div className="grid grid-cols-4 gap-2">
                {([
                  { rating: Rating.Again, label: "Again", desc: "Forgot completely", color: "var(--danger)" },
                  { rating: Rating.Hard, label: "Hard", desc: "Barely remembered", color: "var(--warning)" },
                  { rating: Rating.Good, label: "Good", desc: "Remembered with effort", color: "var(--success)" },
                  { rating: Rating.Easy, label: "Easy", desc: "Knew instantly", color: "var(--accent)" },
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
