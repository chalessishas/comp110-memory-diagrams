"use client";

import { useEffect, useCallback } from "react";
import { useParams } from "next/navigation";
import { useShallow } from "zustand/shallow";
import { usePracticeStore } from "@/stores/practice";
import { QuestionCard } from "@/components/practice/question-card";
import { FeedbackPanel } from "@/components/practice/feedback-panel";
import { SessionComplete } from "@/components/practice/session-complete";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Loader2 } from "lucide-react";

export default function PracticePage() {
  const { id: courseId } = useParams<{ id: string }>();

  const {
    questions,
    currentIndex,
    status,
    error,
    selectedAnswer,
    attemptResult,
    totalAnswered,
    totalCorrect,
    loadQuestions,
    selectAnswer,
    submitAnswer,
    nextQuestion,
    reset,
  } = usePracticeStore(
    useShallow((s) => ({
      questions: s.questions,
      currentIndex: s.currentIndex,
      status: s.status,
      error: s.error,
      selectedAnswer: s.selectedAnswer,
      attemptResult: s.attemptResult,
      totalAnswered: s.totalAnswered,
      totalCorrect: s.totalCorrect,
      loadQuestions: s.loadQuestions,
      selectAnswer: s.selectAnswer,
      submitAnswer: s.submitAnswer,
      nextQuestion: s.nextQuestion,
      reset: s.reset,
    })),
  );

  useEffect(() => {
    if (courseId) loadQuestions(courseId);
    return () => reset();
  }, [courseId, loadQuestions, reset]);

  // Keyboard shortcuts
  const handleKeyDown = useCallback(
    (e: KeyboardEvent) => {
      if (status === "answering") {
        const question = questions[currentIndex];
        if (question?.type === "multiple_choice" && question.options) {
          const key = e.key.toUpperCase();
          const idx = { "1": 0, "2": 1, "3": 2, "4": 3, A: 0, B: 1, C: 2, D: 3 }[key];
          if (idx !== undefined && question.options[idx]) {
            selectAnswer(question.options[idx].label);
            return;
          }
        }
        if (e.key === "Enter" && selectedAnswer) {
          e.preventDefault();
          submitAnswer();
        }
      }
      if (status === "feedback" && e.key === "Enter") {
        e.preventDefault();
        nextQuestion();
      }
    },
    [status, questions, currentIndex, selectedAnswer, selectAnswer, submitAnswer, nextQuestion],
  );

  useEffect(() => {
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [handleKeyDown]);

  const currentQuestion = questions[currentIndex];

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="sticky top-0 z-10 border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
        <div className="mx-auto flex h-14 max-w-2xl items-center justify-between px-4">
          <a
            href={`/courses/${courseId}`}
            className="flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground transition-colors"
          >
            <ArrowLeft className="h-4 w-4" />
            Back
          </a>
          {questions.length > 0 && status !== "complete" && (
            <span className="text-sm text-muted-foreground">
              {currentIndex + 1}/{questions.length}
            </span>
          )}
        </div>
      </header>

      {/* Content */}
      <main className="mx-auto max-w-2xl px-4 py-6">
        {/* Loading */}
        {status === "loading" && !currentQuestion && (
          <div className="flex flex-col items-center justify-center gap-3 py-20">
            <Loader2 className="h-8 w-8 animate-spin text-muted-foreground" />
            <p className="text-sm text-muted-foreground">Loading questions...</p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="rounded-lg border border-destructive/50 bg-destructive/10 p-4 text-center">
            <p className="text-sm text-destructive">{error}</p>
            <Button variant="outline" size="sm" className="mt-3" onClick={() => courseId && loadQuestions(courseId)}>
              Retry
            </Button>
          </div>
        )}

        {/* Answering / Feedback */}
        {currentQuestion && (status === "answering" || status === "feedback" || status === "loading") && (
          <div className="space-y-6">
            <QuestionCard
              question={currentQuestion}
              selectedAnswer={selectedAnswer}
              onSelect={selectAnswer}
              disabled={status === "feedback" || status === "loading"}
              attemptResult={attemptResult}
            />

            {status === "answering" && (
              <Button
                onClick={submitAnswer}
                disabled={!selectedAnswer}
                className="w-full"
                size="lg"
              >
                Check Answer
              </Button>
            )}

            {status === "loading" && currentQuestion && (
              <Button disabled className="w-full" size="lg">
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Checking...
              </Button>
            )}

            {status === "feedback" && attemptResult && (
              <FeedbackPanel
                isCorrect={attemptResult.isCorrect}
                userAnswer={selectedAnswer}
                correctAnswer={attemptResult.correctAnswer}
                explanation={attemptResult.explanation}
                onNext={nextQuestion}
              />
            )}
          </div>
        )}

        {/* Session Complete */}
        {status === "complete" && !error && (
          <SessionComplete
            totalAnswered={totalAnswered}
            totalCorrect={totalCorrect}
            courseId={courseId}
            onRetry={() => courseId && loadQuestions(courseId)}
          />
        )}
      </main>
    </div>
  );
}
