"use client";

import { useState } from "react";
import { Check, X, Bookmark } from "lucide-react";
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

  const userAnswer = question.type === "multiple_choice" || question.type === "true_false"
    ? selected ?? ""
    : textAnswer;

  async function handleSubmit() {
    if (!userAnswer) return;

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
      return {
        borderColor: "var(--success)",
        backgroundColor: "rgba(22, 163, 74, 0.08)",
      };
    }

    if (submitted && isSelected && !isAnswer) {
      return {
        borderColor: "var(--danger)",
        backgroundColor: "rgba(239, 68, 68, 0.08)",
      };
    }

    if (!submitted && isSelected) {
      return {
        borderColor: "var(--accent)",
        backgroundColor: "rgba(91, 108, 240, 0.08)",
      };
    }

    return {
      borderColor: "var(--border)",
      backgroundColor: "white",
    };
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
      <button
        onClick={handleBookmarkToggle}
        className="absolute top-4 right-4 p-1.5 cursor-pointer rounded-lg hover:bg-black/5"
        title={isBookmarked ? "Remove from bank" : "Save to question bank"}
      >
        <Bookmark size={16} fill={isBookmarked ? "var(--accent)" : "none"} style={{ color: "var(--accent)" }} />
      </button>
      <div className="mb-6">
        <div className="ui-kicker mb-3">{t(QUESTION_TYPE_I18N_KEYS[question.type])}</div>
        <p className="text-lg font-medium leading-8">{question.stem}</p>
      </div>

      {(question.type === "multiple_choice" || question.type === "true_false") && question.options && (
        <div className="space-y-3 mb-5">
          {question.options.map((opt) => (
            <button
              key={opt.label}
              onClick={() => !submitted && setSelected(opt.label)}
              disabled={submitted}
              className="w-full text-left px-4 py-4 rounded-[22px] text-sm transition-colors cursor-pointer disabled:cursor-default"
              style={{
                border: "1px solid",
                ...getOptionStyles(opt.label),
              }}
            >
              <span className="inline-flex min-w-8 font-semibold mr-2">{opt.label}.</span>
              {opt.text}
            </button>
          ))}
        </div>
      )}

      {(question.type === "fill_blank" || question.type === "short_answer") && (
        <textarea
          value={textAnswer}
          onChange={(e) => !submitted && setTextAnswer(e.target.value)}
          disabled={submitted}
          placeholder={t("questionCard.typeAnswer")}
          className="ui-textarea text-sm mb-5"
          rows={question.type === "short_answer" ? 4 : 1}
        />
      )}

      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={!userAnswer}
          className="ui-button-primary disabled:opacity-40"
        >
          {t("practice.submit")}
        </button>
      ) : (
        <div className="mt-4">
          <div
            className="flex items-start gap-3 rounded-[24px] px-4 py-4 mb-3"
            style={{
              backgroundColor: isCorrect ? "rgba(22, 163, 74, 0.08)" : "rgba(239, 68, 68, 0.08)",
              color: isCorrect ? "var(--success)" : "var(--danger)",
              border: `1px solid ${isCorrect ? "var(--success)" : "var(--danger)"}`,
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
          {revealedExplanation && (
            <p
              className="text-sm p-4 rounded-[22px]"
              style={{ backgroundColor: "white", color: "var(--text-secondary)", border: "1px solid var(--border)" }}
            >
              {revealedExplanation}
            </p>
          )}
          <div className="mt-3 flex items-center gap-1">
            <span className="text-[10px] mr-1" style={{ color: "var(--text-secondary)" }}>{t("questionCard.report")}</span>
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
                className="px-2 py-0.5 rounded-full text-[10px] cursor-pointer disabled:opacity-40"
                style={{
                  border: "1px solid var(--border)",
                  backgroundColor: feedbackGiven === fb.reason ? "var(--bg-muted)" : "transparent",
                  color: "var(--text-secondary)",
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
