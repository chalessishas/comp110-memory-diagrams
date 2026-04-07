"use client";

import { useState, useEffect, useRef } from "react";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import { Check, X, Loader2, ChevronRight } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { recordActivity } from "@/lib/streaks";
import type { LessonChunk } from "@/types";

interface ChunkLessonProps {
  chunks: LessonChunk[];
  courseId: string;
  lessonId: string;
  totalChunks?: number; // from SSE outline, for accurate progress during streaming
  isStreaming?: boolean; // true while chunks are still arriving
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

export function ChunkLesson({ chunks, courseId, lessonId, totalChunks, isStreaming }: ChunkLessonProps) {
  const { locale } = useI18n();
  const isZh = locale === "zh";
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
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {isZh ? "课程内容加载失败，请重试。" : "Lesson content failed to load. Please try again."}
        </p>
      </div>
    );
  }

  if (isComplete) {
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
      <div>
        <div className="flex items-center gap-3 mb-6">
          <div className="flex-1 h-1 rounded-full overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
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
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {isZh ? "正在生成下一个教学环节..." : "Generating next section..."}
          </p>
        </div>
      </div>
    );
  }
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
          {currentChunkIndex + 1}/{displayTotal}
        </span>
      </div>

      {/* Pretest: show checkpoint BEFORE content (attempt → learn) */}
      {/* Regular: show content BEFORE checkpoint (learn → verify) */}
      {/* Remediation on chunk 0: also show content so student can learn before retry */}
      {(currentChunkIndex > 0 || (currentChunkIndex === 0 && state.showRemediation)) && (
        <div className="ui-panel p-6 mb-4">
          <MarkdownRenderer content={activeContent} />
        </div>
      )}

      {/* Checkpoint */}
      {chunk.checkpoint_type && activePrompt && (
        <div className="ui-panel p-6 mb-4" style={{ borderLeft: `3px solid ${chunk.chunk_index === 0 && !state.submitted ? "var(--warning)" : "var(--accent)"}` }}>
          {chunk.chunk_index === 0 && !state.submitted && (
            <p className="text-xs mb-3 px-3 py-2 rounded-lg" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
              {isZh ? "💡 先试试看——答错没关系，尝试本身就能帮助学习" : "💡 Try first — getting it wrong is fine, the attempt itself helps you learn"}
            </p>
          )}
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
          {(chunk.checkpoint_type === "code" || chunk.checkpoint_type === "open" || chunk.checkpoint_type === "latex" || chunk.checkpoint_type === "fill_blank") && (
            <textarea
              value={state.textAnswer}
              onChange={e => !state.submitted && updateState({ textAnswer: e.target.value })}
              disabled={state.submitted}
              placeholder={chunk.checkpoint_type === "fill_blank"
                ? (isZh ? "填写答案..." : "Fill in the blank...")
                : (isZh ? "输入你的答案..." : "Type your answer...")}
              className="ui-textarea mb-4 text-sm font-mono"
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
                {isZh ? "提交" : "Check"}
              </button>
              {state.showRemediation && (
                <button
                  onClick={() => setCurrentChunkIndex(i => i + 1)}
                  className="text-xs px-3 py-1.5 rounded-lg cursor-pointer"
                  style={{ border: "1px solid var(--border)", color: "var(--text-muted)" }}
                >
                  {isZh ? "跳过，继续" : "Skip, move on"}
                </button>
              )}
            </div>
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
                ) : chunk.checkpoint_type === "open" ? (
                  <>
                    <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
                      {isZh ? "参考答案：" : "Expected answer:"} <strong>{chunk.checkpoint_answer}</strong>
                    </span>
                    {!state.correct && (
                      <div className="flex gap-2 mt-2">
                        <button
                          onClick={() => updateState({ correct: true })}
                          className="text-xs px-3 py-1.5 rounded-lg cursor-pointer"
                          style={{ border: "1px solid var(--success)", color: "var(--success)" }}
                        >
                          {isZh ? "我答对了" : "I got it right"}
                        </button>
                        <button
                          onClick={() => updateState({ showRemediation: true, submitted: false, textAnswer: "" })}
                          className="text-xs px-3 py-1.5 rounded-lg cursor-pointer"
                          style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}
                        >
                          {isZh ? "我需要复习" : "I need to review"}
                        </button>
                      </div>
                    )}
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

      {/* Pretest: show content AFTER checkpoint submission */}
      {chunk.chunk_index === 0 && state.submitted && (
        <div className="ui-panel p-6 mb-4">
          <p className="text-xs font-semibold uppercase tracking-wider mb-3" style={{ color: "var(--accent)" }}>
            {isZh ? "现在来学习" : "Now let's learn"}
          </p>
          <MarkdownRenderer content={activeContent} />
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
