"use client";

import { useState, useEffect, useRef } from "react";
import Link from "next/link";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Check, X, Loader2, ChevronRight, BookOpen, Dumbbell } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { recordActivity } from "@/lib/streaks";
import type { LessonChunk } from "@/types";

interface ChunkLessonProps {
  chunks: LessonChunk[];
  courseId: string;
  lessonId: string;
  totalChunks?: number; // from SSE outline, for accurate progress during streaming
  isStreaming?: boolean; // true while chunks are still arriving
  onBack?: () => void; // navigate back to topic list
}

interface CheckpointState {
  selected: string | null;
  textAnswer: string;
  submitted: boolean;
  correct: boolean;
  attempts: number;
  showRemediation: boolean;
}

const defaultCheckpointState: CheckpointState = {
  selected: null,
  textAnswer: "",
  submitted: false,
  correct: false,
  attempts: 0,
  showRemediation: false,
};

export function ChunkLesson({ chunks, courseId, lessonId, totalChunks, isStreaming, onBack }: ChunkLessonProps) {
  const { t } = useI18n();
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [checkpointState, setCheckpointState] = useState<Record<number, CheckpointState>>({});
  const progressSaved = useRef(false);

  const chunk = chunks[currentChunkIndex];
  const state = checkpointState[currentChunkIndex] ?? defaultCheckpointState;
  const isComplete = chunks.length > 0 && currentChunkIndex >= chunks.length;

  // Save progress to server when lesson is completed
  useEffect(() => {
    if (!isComplete || progressSaved.current) return;
    progressSaved.current = true;

    const results: Record<string, { passed: boolean; attempts: number }> = {};
    for (const [idx, s] of Object.entries(checkpointState)) {
      results[idx] = { passed: s.correct, attempts: s.attempts };
    }

    fetch(`/api/courses/${courseId}/lessons/${lessonId}/progress`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        completed: true,
        lastChunkIndex: chunks.length - 1,
        checkpointResults: results,
      }),
    }).catch(() => {}); // best-effort, don't block UI
  }, [isComplete, courseId, lessonId, checkpointState, chunks.length]);

  if (chunks.length === 0) {
    return (
      <div className="text-center py-16">
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {t("lesson.failedToLoad")}
        </p>
      </div>
    );
  }

  if (isComplete) {
    return (
      <div className="text-center py-16 space-y-4">
        <div className="w-14 h-14 rounded-full flex items-center justify-center mx-auto" style={{ backgroundColor: "var(--success)" }}>
          <Check size={28} color="white" />
        </div>
        <h2 className="text-xl font-semibold" style={{ color: "var(--text-primary)" }}>{t("lesson.complete")}</h2>
        <p className="text-sm" style={{ color: "var(--text-muted)" }}>
          {t("lesson.completeDesc")}
        </p>
        <div className="flex justify-center gap-3 pt-2 flex-wrap">
          {onBack && (
            <button onClick={onBack} className="ui-button-secondary">
              <BookOpen size={14} />
              {t("learn.backToTopics")}
            </button>
          )}
          <Link href={`/course/${courseId}/practice`} className="ui-button-primary">
            <Dumbbell size={14} />
            {t("practice.title")}
          </Link>
        </div>
      </div>
    );
  }

  function updateState(update: Partial<CheckpointState>) {
    setCheckpointState(prev => ({
      ...prev,
      [currentChunkIndex]: { ...(prev[currentChunkIndex] ?? defaultCheckpointState), ...update },
    }));
  }

  function checkAnswer(userAnswer: string, expected: string, type: string): boolean {
    const ua = userAnswer.trim().toLowerCase().replace(/[.,;:!?'"()]/g, "").replace(/\s+/g, " ");
    const ea = expected.trim().toLowerCase().replace(/[.,;:!?'"()]/g, "").replace(/\s+/g, " ");

    // MCQ: exact label match
    if (type === "mcq") return ua === ea;

    // fill_blank: exact or contained match (student might write more context)
    if (type === "fill_blank") {
      if (ua === ea) return true;
      if (ua.includes(ea) || ea.includes(ua)) return true;
      // Numeric: compare as numbers if both parseable
      const uNum = parseFloat(ua), eNum = parseFloat(ea);
      if (!isNaN(uNum) && !isNaN(eNum) && Math.abs(uNum - eNum) < 0.001) return true;
      return false;
    }

    // open: keyword overlap — correct if ≥50% of meaningful answer words found
    const answerWords = ea.split(/\s+/).filter(w => w.length > 3);
    if (answerWords.length === 0) return ua.length > 0; // any non-empty answer passes
    const userWords = new Set(ua.split(/\s+/));
    const matched = answerWords.filter(w => userWords.has(w)).length;
    return matched / answerWords.length >= 0.5;
  }

  function handleSubmitCheckpoint() {
    if (!chunk.checkpoint_type || !chunk.checkpoint_answer) return;
    const userAnswer = chunk.checkpoint_type === "mcq" ? state.selected : state.textAnswer;
    if (!userAnswer) return;

    // Use remediation_answer when in remediation mode and it exists
    const expectedAnswer = (state.showRemediation && chunk.remediation_answer) ? chunk.remediation_answer : chunk.checkpoint_answer;
    const correct = checkAnswer(userAnswer, expectedAnswer, chunk.checkpoint_type);
    updateState({ submitted: true, correct, attempts: state.attempts + 1 });
    recordActivity("question");
  }

  function handleNext() {
    // If wrong and has remediation content → show remediation for retry
    if (state.submitted && !state.correct && state.attempts < 3 && chunk.remediation_question) {
      updateState({ showRemediation: true, submitted: false, selected: null, textAnswer: "" });
    }
    // If wrong on first try and NO remediation → show content as "review before retry"
    else if (state.submitted && !state.correct && state.attempts === 1 && !chunk.remediation_question && !state.showRemediation) {
      updateState({ showRemediation: true, submitted: false, selected: null, textAnswer: "" });
    }
    // Otherwise proceed to next chunk
    else {
      setCurrentChunkIndex(i => i + 1);
    }
  }

  const displayTotal = totalChunks ?? chunks.length;
  const progress = displayTotal > 0 ? ((currentChunkIndex + 1) / displayTotal) * 100 : 0;

  // Streaming: chunk not yet available — show loading
  if (!chunk && isStreaming) {
    return (
      <div className="space-y-8">
        {/* Progress bar */}
        <div className="flex items-center gap-3">
          <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: "var(--bg-muted)" }}>
            <div
              className="h-full rounded-full transition-all duration-300"
              style={{ width: `${progress}%`, backgroundColor: "var(--accent)" }}
            />
          </div>
          <span className="text-xs font-medium" style={{ color: "var(--text-muted)" }}>
            {currentChunkIndex + 1}/{displayTotal}
          </span>
        </div>
        <div className="text-center py-12">
          <Loader2 size={20} className="animate-spin mx-auto mb-3" style={{ color: "var(--accent)" }} />
          <p className="text-sm" style={{ color: "var(--text-muted)" }}>
            {t("lesson.generating")}
          </p>
        </div>
      </div>
    );
  }
  const canProceed = !chunk.checkpoint_type || state.submitted;
  const activeContent = state.showRemediation && chunk.remediation_content ? chunk.remediation_content : chunk.content;
  const activePrompt = state.showRemediation && chunk.remediation_question ? chunk.remediation_question : chunk.checkpoint_prompt;

  return (
    <div className="space-y-6">
      {/* Progress bar — thicker, muted track */}
      <div className="flex items-center gap-3">
        <div className="flex-1 h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: "var(--bg-muted)" }}>
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{ width: `${progress}%`, backgroundColor: "var(--accent)" }}
          />
        </div>
        <span className="text-xs font-medium" style={{ color: "var(--text-muted)" }}>
          {currentChunkIndex + 1}/{displayTotal}
        </span>
      </div>

      {/* Content panel — generous whitespace */}
      {(currentChunkIndex > 0 || (currentChunkIndex === 0 && state.showRemediation)) && (
        <div className="ui-panel p-6 md:p-8">
          <MarkdownRenderer content={activeContent} terms={chunk.key_terms} />
        </div>
      )}

      {/* Checkpoint area — subtle muted background */}
      {chunk.checkpoint_type && activePrompt && (
        <div
          className="rounded-[20px] p-6 md:p-8 space-y-5"
          style={{
            backgroundColor: "var(--bg-muted)",
            borderLeft: `3px solid ${chunk.chunk_index === 0 && !state.submitted ? "var(--warning)" : "var(--accent)"}`,
          }}
        >
          {/* Pretest hint */}
          {chunk.chunk_index === 0 && !state.submitted && (
            <p
              className="text-xs px-4 py-2.5 rounded-xl"
              style={{ backgroundColor: "var(--bg-surface)", color: "var(--text-muted)" }}
            >
              {t("lesson.pretestHint")}
            </p>
          )}

          <p className="text-sm font-semibold" style={{ color: "var(--text-primary)" }}>{activePrompt}</p>

          {/* MCQ options — pill-shaped, no border */}
          {chunk.checkpoint_type === "mcq" && chunk.checkpoint_options && (
            <div className="space-y-2.5">
              {chunk.checkpoint_options.map(opt => {
                const isCorrectOpt = opt.label.toLowerCase() === chunk.checkpoint_answer?.trim().toLowerCase();
                const isSelected = state.selected === opt.label;
                let bgColor = "var(--bg-surface)";
                let textColor = "var(--text-primary)";

                if (state.submitted) {
                  if (isCorrectOpt) {
                    bgColor = "var(--accent-light)";
                    textColor = "var(--success)";
                  } else if (isSelected) {
                    bgColor = "var(--bg-surface)";
                    textColor = "var(--danger)";
                  }
                } else if (isSelected) {
                  bgColor = "var(--accent-light)";
                }

                return (
                  <button
                    key={opt.label}
                    onClick={() => !state.submitted && updateState({ selected: opt.label })}
                    disabled={state.submitted}
                    className="w-full text-left px-5 py-3.5 rounded-[16px] text-sm cursor-pointer disabled:cursor-default transition-all"
                    style={{ backgroundColor: bgColor, color: textColor }}
                  >
                    <span className="font-medium mr-2" style={{ color: "var(--accent)" }}>{opt.label}.</span>{opt.text}
                  </button>
                );
              })}
            </div>
          )}

          {/* Text/code/open/latex input */}
          {(chunk.checkpoint_type === "code" || chunk.checkpoint_type === "open" || chunk.checkpoint_type === "latex" || chunk.checkpoint_type === "fill_blank") && (
            <textarea
              value={state.textAnswer}
              onChange={e => !state.submitted && updateState({ textAnswer: e.target.value })}
              disabled={state.submitted}
              placeholder={chunk.checkpoint_type === "fill_blank"
                ? (t("lesson.fillBlank"))
                : (t("lesson.typeAnswer"))}
              className="ui-textarea text-sm font-mono"
              rows={chunk.checkpoint_type === "fill_blank" ? 1 : 3}
            />
          )}

          {/* Submit / Result */}
          {!state.submitted ? (
            <div className="flex items-center gap-3">
              <button
                onClick={handleSubmitCheckpoint}
                disabled={!state.selected && !state.textAnswer}
                className="ui-button-primary disabled:opacity-30"
              >
                {t("lesson.check")}
              </button>
              {state.showRemediation && (
                <button
                  onClick={() => setCurrentChunkIndex(i => i + 1)}
                  className="ui-button-ghost text-xs"
                  style={{ color: "var(--text-muted)" }}
                >
                  {t("lesson.skipMoveOn")}
                </button>
              )}
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2 flex-wrap">
                {state.correct ? (
                  <>
                    <Check size={16} style={{ color: "var(--success)" }} />
                    <span className="text-sm font-medium" style={{ color: "var(--success)" }}>
                      {t("lesson.correct")}
                    </span>
                  </>
                ) : chunk.checkpoint_type === "open" ? (
                  <div className="space-y-2">
                    <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
                      {t("lesson.expectedAnswer")} <span className="font-semibold">{chunk.checkpoint_answer}</span>
                    </span>
                    {!state.correct && (
                      <div className="flex gap-2">
                        <button
                          onClick={() => updateState({ correct: true })}
                          className="ui-button-ghost text-xs"
                          style={{ color: "var(--success)" }}
                        >
                          {t("lesson.iGotItRight")}
                        </button>
                        <button
                          onClick={() => updateState({ showRemediation: true, submitted: false, textAnswer: "" })}
                          className="ui-button-ghost text-xs"
                          style={{ color: "var(--text-muted)" }}
                        >
                          {t("lesson.iNeedReview")}
                        </button>
                      </div>
                    )}
                  </div>
                ) : (
                  <>
                    <X size={16} style={{ color: "var(--danger)" }} />
                    <span className="text-sm font-medium" style={{ color: "var(--danger)" }}>
                      {t("lesson.notQuite")} -- {chunk.checkpoint_answer}
                    </span>
                  </>
                )}
              </div>

              {!state.correct && state.attempts >= 3 && (
                <div
                  className="p-4 rounded-[16px] text-xs"
                  style={{ backgroundColor: "var(--bg-surface)", color: "var(--text-muted)" }}
                >
                  {t("lesson.keepGoing")}
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Pretest: show content AFTER checkpoint submission */}
      {chunk.chunk_index === 0 && state.submitted && (
        <div className="ui-panel p-6 md:p-8">
          <p className="ui-kicker mb-4" style={{ color: "var(--accent)" }}>
            {t("lesson.nowLearn")}
          </p>
          <MarkdownRenderer content={activeContent} terms={chunk.key_terms} />
        </div>
      )}

      {/* Navigation — ghost button, right-aligned */}
      {canProceed && (
        <div className="flex justify-end pt-2">
          <button onClick={handleNext} className="ui-button-primary">
            {currentChunkIndex === chunks.length - 1
              ? (t("lesson.finish"))
              : (t("lesson.continue"))}
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
