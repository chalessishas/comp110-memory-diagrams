"use client";

import { useState } from "react";
import { Check, X } from "lucide-react";
import type { Question } from "@/types";

interface QuestionCardProps {
  question: Question;
  onAnswer: (questionId: string, answer: string, isCorrect: boolean) => void;
}

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

  return (
    <div className="p-6 rounded-xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
      <p className="text-sm font-medium mb-4">{question.stem}</p>

      {(question.type === "multiple_choice" || question.type === "true_false") && question.options && (
        <div className="space-y-2 mb-4">
          {question.options.map((opt) => (
            <button
              key={opt.label}
              onClick={() => !submitted && setSelected(opt.label)}
              disabled={submitted}
              className="w-full text-left px-4 py-3 rounded-lg text-sm transition-colors cursor-pointer disabled:cursor-default"
              style={{
                border: "1px solid",
                borderColor: submitted
                  ? opt.label.toLowerCase() === question.answer.trim().toLowerCase()
                    ? "var(--success)"
                    : selected === opt.label
                      ? "var(--danger)"
                      : "var(--border)"
                  : selected === opt.label
                    ? "var(--accent)"
                    : "var(--border)",
                backgroundColor: submitted
                  ? opt.label.toLowerCase() === question.answer.trim().toLowerCase()
                    ? "rgba(74, 124, 89, 0.1)"
                    : "transparent"
                  : selected === opt.label
                    ? "rgba(196, 169, 125, 0.1)"
                    : "transparent",
              }}
            >
              <span className="font-medium mr-2">{opt.label}.</span>
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
          className="w-full px-4 py-3 rounded-lg text-sm mb-4 resize-none"
          style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-primary)" }}
          rows={question.type === "short_answer" ? 4 : 1}
        />
      )}

      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={!userAnswer}
          className="px-6 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-40"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          Submit
        </button>
      ) : (
        <div className="mt-4">
          <div className="flex items-center gap-2 mb-2">
            {isCorrect ? (
              <><Check size={16} style={{ color: "var(--success)" }} /><span className="text-sm font-medium" style={{ color: "var(--success)" }}>Correct</span></>
            ) : (
              <><X size={16} style={{ color: "var(--danger)" }} /><span className="text-sm font-medium" style={{ color: "var(--danger)" }}>Incorrect — answer: {question.answer}</span></>
            )}
          </div>
          {question.explanation && (
            <p className="text-sm p-3 rounded-lg" style={{ backgroundColor: "var(--bg-primary)", color: "var(--text-secondary)" }}>
              {question.explanation}
            </p>
          )}
        </div>
      )}
    </div>
  );
}
