"use client";

import { cn } from "@/lib/utils";
import type { Question } from "@/types";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";

interface QuestionCardProps {
  question: Question;
  selectedAnswer: string;
  onSelect: (answer: string) => void;
  disabled?: boolean;
  attemptResult?: { isCorrect: boolean; correctAnswer: string } | null;
}

function Stem({ text }: { text: string }) {
  return (
    <div className="text-lg leading-relaxed text-foreground">
      <ReactMarkdown remarkPlugins={[remarkMath, remarkGfm]} rehypePlugins={[rehypeKatex]}>
        {text}
      </ReactMarkdown>
    </div>
  );
}

function MCQOptions({
  options,
  selected,
  onSelect,
  disabled,
  correctAnswer,
}: {
  options: { label: string; text: string }[];
  selected: string;
  onSelect: (answer: string) => void;
  disabled?: boolean;
  correctAnswer?: string;
}) {
  return (
    <div role="radiogroup" aria-label="Answer options" className="flex flex-col gap-3">
      {options.map((opt) => {
        const isSelected = selected === opt.label;
        const isCorrect = correctAnswer === opt.label;
        const isWrongSelected = isSelected && correctAnswer && !isCorrect;

        return (
          <button
            key={opt.label}
            role="radio"
            aria-checked={isSelected}
            disabled={disabled}
            onClick={() => onSelect(opt.label)}
            className={cn(
              "flex items-start gap-3 rounded-lg border px-4 py-3 text-left transition-all",
              "min-h-[48px] touch-manipulation",
              "hover:border-primary/50 hover:bg-accent/50",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              isSelected && !correctAnswer && "border-primary bg-primary/5",
              isCorrect && "border-success bg-success/10",
              isWrongSelected && "border-destructive bg-destructive/10 animate-shake",
              disabled && !isCorrect && !isWrongSelected && "opacity-50",
            )}
          >
            <span
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-full border text-sm font-medium",
                isSelected && !correctAnswer && "border-primary bg-primary text-primary-foreground",
                isCorrect && "border-success bg-success text-success-foreground",
                isWrongSelected && "border-destructive bg-destructive text-destructive-foreground",
                !isSelected && !isCorrect && "border-muted-foreground/30",
              )}
            >
              {opt.label}
            </span>
            <span className="pt-0.5 text-sm leading-relaxed">
              <ReactMarkdown remarkPlugins={[remarkMath, remarkGfm]} rehypePlugins={[rehypeKatex]}>
                {opt.text}
              </ReactMarkdown>
            </span>
          </button>
        );
      })}
    </div>
  );
}

function TrueFalseInput({
  selected,
  onSelect,
  disabled,
  correctAnswer,
}: {
  selected: string;
  onSelect: (answer: string) => void;
  disabled?: boolean;
  correctAnswer?: string;
}) {
  return (
    <div className="grid grid-cols-2 gap-3">
      {["True", "False"].map((val) => {
        const isSelected = selected === val;
        const isCorrect = correctAnswer?.toLowerCase() === val.toLowerCase();
        const isWrongSelected = isSelected && correctAnswer && !isCorrect;

        return (
          <button
            key={val}
            disabled={disabled}
            onClick={() => onSelect(val)}
            className={cn(
              "rounded-lg border py-4 text-center text-base font-medium transition-all",
              "touch-manipulation",
              "hover:border-primary/50 hover:bg-accent/50",
              "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
              isSelected && !correctAnswer && "border-primary bg-primary/5",
              isCorrect && "border-success bg-success/10 text-success",
              isWrongSelected && "border-destructive bg-destructive/10 text-destructive",
            )}
          >
            {val}
          </button>
        );
      })}
    </div>
  );
}

function TextInput({
  selected,
  onSelect,
  disabled,
  multiline,
}: {
  selected: string;
  onSelect: (answer: string) => void;
  disabled?: boolean;
  multiline?: boolean;
}) {
  const Component = multiline ? "textarea" : "input";
  return (
    <Component
      value={selected}
      onChange={(e) => onSelect(e.target.value)}
      disabled={disabled}
      placeholder={multiline ? "Type your answer..." : "Your answer"}
      aria-label="Your answer"
      autoFocus
      rows={multiline ? 3 : undefined}
      className={cn(
        "w-full rounded-lg border border-input bg-background px-4 py-3 text-base",
        "placeholder:text-muted-foreground",
        "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring",
        "disabled:opacity-50",
        multiline && "min-h-[80px] resize-y",
      )}
    />
  );
}

export function QuestionCard({ question, selectedAnswer, onSelect, disabled, attemptResult }: QuestionCardProps) {
  const correctAnswer = attemptResult?.correctAnswer;

  return (
    <div className="space-y-6">
      <Stem text={question.stem} />

      {question.type === "multiple_choice" && question.options && (
        <MCQOptions
          options={question.options}
          selected={selectedAnswer}
          onSelect={onSelect}
          disabled={disabled}
          correctAnswer={correctAnswer}
        />
      )}

      {question.type === "true_false" && (
        <TrueFalseInput
          selected={selectedAnswer}
          onSelect={onSelect}
          disabled={disabled}
          correctAnswer={correctAnswer}
        />
      )}

      {question.type === "fill_blank" && (
        <TextInput selected={selectedAnswer} onSelect={onSelect} disabled={disabled} />
      )}

      {question.type === "short_answer" && (
        <TextInput selected={selectedAnswer} onSelect={onSelect} disabled={disabled} multiline />
      )}
    </div>
  );
}
