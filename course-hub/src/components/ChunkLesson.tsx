"use client";

import { useState } from "react";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Check, X, Loader2, ChevronRight } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { recordActivity } from "@/lib/streaks";
import type { LessonChunk } from "@/types";

interface ChunkLessonProps {
  chunks: LessonChunk[];
  courseId: string;
  lessonId: string;
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

export function ChunkLesson({ chunks, courseId: _courseId, lessonId: _lessonId }: ChunkLessonProps) {
  const { locale } = useI18n();
  const isZh = locale === "zh";
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [checkpointState, setCheckpointState] = useState<Record<number, CheckpointState>>({});

  const chunk = chunks[currentChunkIndex];
  const state = checkpointState[currentChunkIndex] ?? defaultCheckpointState;

  if (!chunk) {
    return (
      <div className="text-center py-16">
        <Check size={40} className="mx-auto mb-4" style={{ color: "var(--success)" }} />
        <h2 className="text-xl font-semibold mb-2">{isZh ? "课程完成！" : "Lesson Complete!"}</h2>
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {isZh ? "做得好。这节课的内容已经学完了。" : "Well done. You've completed this lesson."}
        </p>
      </div>
    );
  }

  function updateState(update: Partial<CheckpointState>) {
    setCheckpointState(prev => ({
      ...prev,
      [currentChunkIndex]: { ...(prev[currentChunkIndex] ?? defaultCheckpointState), ...update },
    }));
  }

  function handleSubmitCheckpoint() {
    if (!chunk.checkpoint_type || !chunk.checkpoint_answer) return;
    const userAnswer = chunk.checkpoint_type === "mcq" ? state.selected : state.textAnswer;
    if (!userAnswer) return;

    const correct = userAnswer.trim().toLowerCase() === chunk.checkpoint_answer.trim().toLowerCase();
    updateState({ submitted: true, correct, attempts: state.attempts + 1 });
    recordActivity("question");
  }

  function handleNext() {
    if (state.submitted && !state.correct && state.attempts < 3 && chunk.remediation_question) {
      updateState({ showRemediation: true, submitted: false, selected: null, textAnswer: "" });
    } else {
      setCurrentChunkIndex(i => i + 1);
    }
  }

  const progress = chunks.length > 0 ? ((currentChunkIndex + 1) / chunks.length) * 100 : 0;
  const canProceed = !chunk.checkpoint_type || state.submitted;
  const activeContent = state.showRemediation && chunk.remediation_content ? chunk.remediation_content : chunk.content;
  const activePrompt = state.showRemediation && chunk.remediation_question ? chunk.remediation_question : chunk.checkpoint_prompt;

  return (
    <div>
      {/* Progress bar */}
      <div className="flex items-center gap-3 mb-6">
        <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
          <div
            className="h-full rounded-full transition-all duration-300"
            style={{ width: `${progress}%`, backgroundColor: "var(--accent)" }}
          />
        </div>
        <span className="text-xs font-medium" style={{ color: "var(--text-muted)" }}>
          {currentChunkIndex + 1}/{chunks.length}
        </span>
      </div>

      {/* Chunk content */}
      <div className="ui-panel p-6 mb-4">
        <MarkdownRenderer content={activeContent} />
      </div>

      {/* Checkpoint */}
      {chunk.checkpoint_type && activePrompt && (
        <div className="ui-panel p-6 mb-4" style={{ borderLeft: "3px solid var(--accent)" }}>
          <p className="text-sm font-semibold mb-4">{activePrompt}</p>

          {/* MCQ options */}
          {chunk.checkpoint_type === "mcq" && chunk.checkpoint_options && (
            <div className="space-y-2 mb-4">
              {chunk.checkpoint_options.map(opt => {
                const isCorrect = opt.label.toLowerCase() === chunk.checkpoint_answer?.trim().toLowerCase();
                const isSelected = state.selected === opt.label;
                let borderColor = "var(--border)";
                let bgColor = "transparent";

                if (state.submitted) {
                  if (isCorrect) {
                    borderColor = "var(--success)";
                    bgColor = "rgba(5, 150, 105, 0.06)";
                  } else if (isSelected) {
                    borderColor = "var(--danger)";
                  }
                } else if (isSelected) {
                  borderColor = "var(--accent)";
                  bgColor = "var(--accent-light)";
                }

                return (
                  <button
                    key={opt.label}
                    onClick={() => !state.submitted && updateState({ selected: opt.label })}
                    disabled={state.submitted}
                    className="w-full text-left px-4 py-3 rounded-lg text-sm cursor-pointer disabled:cursor-default transition-colors"
                    style={{ border: "1px solid", borderColor, backgroundColor: bgColor }}
                  >
                    <span className="font-medium mr-2">{opt.label}.</span>{opt.text}
                  </button>
                );
              })}
            </div>
          )}

          {/* Text/code/open/latex input */}
          {(chunk.checkpoint_type === "code" || chunk.checkpoint_type === "open" || chunk.checkpoint_type === "latex") && (
            <textarea
              value={state.textAnswer}
              onChange={e => !state.submitted && updateState({ textAnswer: e.target.value })}
              disabled={state.submitted}
              placeholder={isZh ? "输入你的答案..." : "Type your answer..."}
              className="ui-textarea mb-4 min-h-[80px] text-sm font-mono"
            />
          )}

          {/* Submit / Result */}
          {!state.submitted ? (
            <button
              onClick={handleSubmitCheckpoint}
              disabled={!state.selected && !state.textAnswer}
              className="ui-button-primary disabled:opacity-30"
            >
              {isZh ? "提交" : "Check"}
            </button>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                {state.correct ? (
                  <>
                    <Check size={16} style={{ color: "var(--success)" }} />
                    <span className="text-sm font-medium" style={{ color: "var(--success)" }}>
                      {isZh ? "正确" : "Correct"}
                    </span>
                  </>
                ) : (
                  <>
                    <X size={16} style={{ color: "var(--danger)" }} />
                    <span className="text-sm font-medium" style={{ color: "var(--danger)" }}>
                      {isZh ? "不太对" : "Not quite"} — {chunk.checkpoint_answer}
                    </span>
                  </>
                )}
              </div>

              {!state.correct && state.attempts >= 3 && (
                <div className="p-3 rounded-lg text-xs" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <p style={{ color: "var(--text-secondary)" }}>
                    {isZh
                      ? "没关系，继续前进。这个知识点会在后续复习中重新出现。"
                      : "That's okay. Keep going — this topic will come back in review."}
                  </p>
                </div>
              )}
            </div>
          )}
        </div>
      )}

      {/* Next button */}
      {canProceed && (
        <div className="flex justify-end">
          <button onClick={handleNext} className="ui-button-primary">
            {currentChunkIndex === chunks.length - 1
              ? (isZh ? "完成" : "Finish")
              : (isZh ? "继续" : "Continue")}
            <ChevronRight size={16} />
          </button>
        </div>
      )}
    </div>
  );
}
