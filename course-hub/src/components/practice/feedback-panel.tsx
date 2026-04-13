"use client";

import { cn } from "@/lib/utils";
import { CheckCircle, XCircle, Bookmark, Flag } from "lucide-react";
import { Button } from "@/components/ui/button";
import ReactMarkdown from "react-markdown";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";
import remarkGfm from "remark-gfm";

interface FeedbackPanelProps {
  isCorrect: boolean;
  userAnswer: string;
  correctAnswer: string;
  explanation: string | null;
  onNext: () => void;
  onBookmark?: () => void;
  onReport?: () => void;
}

export function FeedbackPanel({
  isCorrect,
  userAnswer,
  correctAnswer,
  explanation,
  onNext,
  onBookmark,
  onReport,
}: FeedbackPanelProps) {
  return (
    <div className="space-y-4" aria-live="polite">
      {/* Result banner */}
      <div
        className={cn(
          "flex items-center gap-2 rounded-lg px-4 py-3 font-medium",
          isCorrect ? "bg-success/10 text-success" : "bg-destructive/10 text-destructive",
        )}
      >
        {isCorrect ? <CheckCircle className="h-5 w-5" /> : <XCircle className="h-5 w-5" />}
        {isCorrect ? "Correct!" : "Incorrect"}
      </div>

      {/* Answer comparison (only when wrong) */}
      {!isCorrect && (
        <div className="space-y-1 text-sm">
          <p className="text-muted-foreground">
            Your answer: <span className="text-destructive font-medium">{userAnswer}</span>
          </p>
          <p className="text-muted-foreground">
            Correct answer: <span className="text-success font-medium">{correctAnswer}</span>
          </p>
        </div>
      )}

      {/* Explanation */}
      {explanation && (
        <div className="rounded-lg border bg-card p-4">
          <p className="mb-2 text-xs font-medium uppercase tracking-wider text-muted-foreground">
            Explanation
            <span className="ml-2 rounded bg-muted px-1.5 py-0.5 text-[10px]">AI Generated</span>
          </p>
          <div className="prose prose-sm dark:prose-invert max-w-none text-sm leading-relaxed">
            <ReactMarkdown remarkPlugins={[remarkMath, remarkGfm]} rehypePlugins={[rehypeKatex]}>
              {explanation}
            </ReactMarkdown>
          </div>
        </div>
      )}

      {/* Action row */}
      <div className="flex items-center gap-2">
        {onBookmark && (
          <Button variant="ghost" size="sm" onClick={onBookmark}>
            <Bookmark className="mr-1 h-4 w-4" />
            Bookmark
          </Button>
        )}
        {onReport && (
          <Button variant="ghost" size="sm" onClick={onReport}>
            <Flag className="mr-1 h-4 w-4" />
            Report
          </Button>
        )}
      </div>

      {/* Next button */}
      <Button onClick={onNext} className="w-full" size="lg">
        Next Question
      </Button>
    </div>
  );
}
