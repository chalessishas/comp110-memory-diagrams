"use client";

import { useState } from "react";
import { Check, X } from "lucide-react";
import type { Question } from "@/types";

interface QuestionCardProps {
  question: Question;
  onAnswer: (questionId: string, answer: string, isCorrect: boolean) => void;
}

const QUESTION_TYPE_LABELS: Record<Question["type"], string> = {
  multiple_choice: "Multiple Choice",
  true_false: "True or False",
  fill_blank: "Fill in the Blank",
  short_answer: "Short Answer",
};

export function QuestionCard({ question, onAnswer }: QuestionCardProps) {
  const [selected, setSelected] = useState<string | null>(null);
  const [submitted, setSubmitted] = useState(false);
  const [textAnswer, setTextAnswer] = useState("");

  const userAnswer = question.type === "multiple_choice" || question.type === "true_false"
    ? selected ?? ""
    : textAnswer;

  const isCorrect = submitted && userAnswer.trim().toLowerCase() === question.answer.trim().toLowerCase();

  async function handleSubmit() {
    if (!userAnswer) return;

    const correct = userAnswer.trim().toLowerCase() === question.answer.trim().toLowerCase();
    setSubmitted(true);

    await fetch("/api/attempts", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: question.id, user_answer: userAnswer }),
    });

    onAnswer(question.id, userAnswer, correct);
  }

  function getOptionStyles(optionLabel: string) {
    const normalizedLabel = optionLabel.toLowerCase();
    const normalizedAnswer = question.answer.trim().toLowerCase();
    const isAnswer = normalizedLabel === normalizedAnswer;
    const isSelected = selected === optionLabel;

    if (submitted && isAnswer) {
      return {
        borderColor: "var(--accent)",
        backgroundColor: "rgba(16, 16, 16, 0.06)",
      };
    }

    if (submitted && isSelected && !isAnswer) {
      return {
        borderColor: "var(--border-strong)",
        backgroundColor: "rgba(0, 0, 0, 0.03)",
      };
    }

    if (!submitted && isSelected) {
      return {
        borderColor: "var(--accent)",
        backgroundColor: "rgba(16, 16, 16, 0.04)",
      };
    }

    return {
      borderColor: "var(--border)",
      backgroundColor: "white",
    };
  }

  return (
    <div className="ui-panel p-6 md:p-8">
      <div className="mb-6">
        <div className="ui-kicker mb-3">{QUESTION_TYPE_LABELS[question.type]}</div>
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
          placeholder="Type your answer..."
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
          Submit
        </button>
      ) : (
        <div className="mt-4">
          <div
            className="flex items-start gap-3 rounded-[24px] px-4 py-4 mb-3"
            style={{
              backgroundColor: isCorrect ? "var(--accent)" : "var(--bg-muted)",
              color: isCorrect ? "white" : "var(--text-primary)",
              border: `1px solid ${isCorrect ? "var(--accent)" : "var(--border)"}`,
            }}
          >
            {isCorrect ? (
              <>
                <Check size={18} />
                <span className="text-sm font-medium">Correct</span>
              </>
            ) : (
              <>
                <X size={18} style={{ color: "var(--text-secondary)" }} />
                <span className="text-sm font-medium">
                  Incorrect. Correct answer: {question.answer}
                </span>
              </>
            )}
          </div>
          {question.explanation && (
            <p
              className="text-sm p-4 rounded-[22px]"
              style={{ backgroundColor: "white", color: "var(--text-secondary)", border: "1px solid var(--border)" }}
            >
              {question.explanation}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
