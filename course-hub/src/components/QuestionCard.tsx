"use client";

import { useState } from "react";
import { Check, X, Bookmark, Loader2 } from "lucide-react";
import type { Question } from "@/types";
import { updateCard, Rating } from "@/lib/spaced-repetition";
import { recordActivity } from "@/lib/streaks";
import { useI18n } from "@/lib/i18n";

interface QuestionCardProps {
  question: Question;
  onAnswer: (questionId: string, answer: string, isCorrect: boolean) => void;
  bookmarked?: boolean;
}

// Type labels are now rendered via i18n keys in the component

const QUESTION_TYPE_I18N_KEYS: Record<Question["type"], string> = {
  multiple_choice: "questionCard.multipleChoice",
  true_false: "questionCard.trueFalse",
  fill_blank: "questionCard.fillBlank",
  short_answer: "questionCard.shortAnswer",
};

export function QuestionCard({ question, onAnswer, bookmarked: initialBookmarked }: QuestionCardProps) {
  const { t } = useI18n();
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [textAnswer, setTextAnswer] = useState("");
  const [isBookmarked, setIsBookmarked] = useState(initialBookmarked ?? false);
  const [feedbackGiven, setFeedbackGiven] = useState<string | null>(null);
  // Answer + explanation are revealed only after server-side grading
  const [revealedAnswer, setRevealedAnswer] = useState<string | null>(null);
  const [revealedExplanation, setRevealedExplanation] = useState<string | null>(null);
  const [isCorrect, setIsCorrect] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const userAnswer = question.type === "multiple_choice" || question.type === "true_false"
    ? selected ?? ""
    : textAnswer;

  async function handleSubmit() {
    if (!userAnswer || submitting) return;
    setSubmitting(true);

    const res = await fetch("/api/attempts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: question.id, user_answer: userAnswer }),
    });

    const data = await res.json();
    const correct = data.is_correct ?? false;

    setIsCorrect(correct);
    setRevealedAnswer(data.correct_answer ?? null);
    setRevealedExplanation(data.explanation ?? null);
    setSubmitted(true);

    // Add to spaced repetition review queue
    updateCard(question.id, correct ? Rating.Good : Rating.Again);
    recordActivity("question");

    onAnswer(question.id, userAnswer, correct);
  }

  function getOptionStyles(optionLabel: string) {
    const normalizedLabel = optionLabel.toLowerCase();
    const normalizedAnswer = (revealedAnswer ?? "").trim().toLowerCase();
    const isAnswer = submitted && normalizedLabel === normalizedAnswer;
    const isSelected = selected === optionLabel;

    if (submitted && isAnswer) {
      return { backgroundColor: "var(--accent-light)", color: "var(--success)" };
    }

    if (submitted && isSelected && !isAnswer) {
      return { backgroundColor: "var(--bg-muted)", color: "var(--danger)" };
    }

    if (!submitted && isSelected) {
      return { backgroundColor: "var(--accent-light)", color: "var(--text-primary)" };
    }

    return { backgroundColor: "var(--bg-surface)", color: "var(--text-primary)" };
  }

  async function handleBookmarkToggle() {
    if (isBookmarked) {
      await fetch("/api/bookmarks", {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: question.id }),
      });
      setIsBookmarked(false);
    } else {
      await fetch("/api/bookmarks", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question_id: question.id }),
      });
      setIsBookmarked(true);
    }
  }

  return (
    <div className="ui-panel p-6 md:p-8 relative">
      {/* Bookmark */}
      <button
        onClick={handleBookmarkToggle}
        className="absolute top-5 right-5 p-2 cursor-pointer rounded-xl transition-colors"
        style={{ color: "var(--accent)" }}
        title={isBookmarked ? "Remove from bank" : "Save to question bank"}
      >
        <Bookmark size={16} fill={isBookmarked ? "var(--accent)" : "none"} />
      </button>

      {/* Question stem */}
      <div className="mb-8">
        <div className="ui-kicker mb-3">{t(QUESTION_TYPE_I18N_KEYS[question.type])}</div>
        <p className="text-lg font-medium leading-relaxed" style={{ color: "var(--text-primary)" }}>{question.stem}</p>
      </div>

      {/* MCQ / T-F options — pill-shaped, no border */}
      {(question.type === "multiple_choice" || question.type === "true_false") && question.options && (
        <div className="space-y-3 mb-6">
          {question.options.map((opt) => (
            <button
              key={opt.label}
              onClick={() => !submitted && setSelected(opt.label)}
              disabled={submitted}
              className="w-full text-left px-5 py-4 rounded-[20px] text-sm transition-all cursor-pointer disabled:cursor-default"
              style={getOptionStyles(opt.label)}
            >
              <span className="inline-flex min-w-8 font-semibold mr-2" style={{ color: "var(--accent)" }}>{opt.label}.</span>
              {opt.text}
            </button>
          ))}
        </div>
      )}

      {/* Fill-blank / short-answer */}
      {(question.type === "fill_blank" || question.type === "short_answer") && (
        <textarea
          value={textAnswer}
          onChange={(e) => !submitted && setTextAnswer(e.target.value)}
          disabled={submitted}
          placeholder={t("questionCard.typeAnswer")}
          className="ui-textarea text-sm mb-6"
          rows={question.type === "short_answer" ? 4 : 1}
        />
      )}

      {/* Submit or feedback */}
      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={!userAnswer || submitting}
          className="ui-button-primary disabled:opacity-40"
        >
          {submitting ? <Loader2 size={16} className="animate-spin" /> : t("practice.submit")}
        </button>
      ) : (
        <div className="mt-6 space-y-4">
          {/* Correct / wrong feedback — soft bg, no harsh border */}
          <div
            className="flex items-center gap-3 rounded-[20px] px-5 py-4"
            style={{
              backgroundColor: isCorrect ? "var(--accent-light)" : "var(--bg-muted)",
              color: isCorrect ? "var(--success)" : "var(--danger)",
            }}
          >
            {isCorrect ? (
              <>
                <Check size={18} />
                <span className="text-sm font-medium">{t("practice.correct")}</span>
              </>
            ) : (
              <>
                <X size={18} />
                <span className="text-sm font-medium">
                  {t("questionCard.incorrectAnswer")} {revealedAnswer}
                </span>
              </>
            )}
          </div>

          {/* Explanation — subtle left accent bar */}
          {revealedExplanation && (
            <div
              className="text-sm py-4 px-5 rounded-[16px]"
              style={{
                backgroundColor: "var(--bg-muted)",
                color: "var(--text-secondary)",
                borderLeft: "3px solid var(--accent)",
              }}
            >
              {revealedExplanation}
            </div>
          )}

          {/* Feedback pills */}
          <div className="flex items-center gap-1.5 flex-wrap">
            <span className="text-[11px] mr-1" style={{ color: "var(--text-muted)" }}>{t("questionCard.report")}</span>
            {[
              { reason: "wrong_answer", label: t("questionCard.reportWrong") },
              { reason: "unclear", label: t("questionCard.reportUnclear") },
              { reason: "too_easy", label: t("questionCard.reportTooEasy") },
              { reason: "too_hard", label: t("questionCard.reportTooHard") },
            ].map((fb) => (
              <button
                key={fb.reason}
                onClick={async () => {
                  await fetch(`/api/questions/${question.id}/feedback`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ reason: fb.reason }),
                  });
                  setFeedbackGiven(fb.reason);
                }}
                disabled={!!feedbackGiven}
                className="px-2.5 py-1 rounded-lg text-[11px] cursor-pointer disabled:opacity-40 transition-colors"
                style={{
                  backgroundColor: feedbackGiven === fb.reason ? "var(--accent-light)" : "var(--bg-muted)",
                  color: "var(--text-muted)",
                }}
              >
                {fb.label}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
