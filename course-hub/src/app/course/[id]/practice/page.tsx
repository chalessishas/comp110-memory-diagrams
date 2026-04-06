"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { FileDropzone } from "@/components/FileDropzone";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { ChevronLeft, ChevronRight, Loader2, Upload, ArrowLeft, Sparkles } from "lucide-react";
import type { Question } from "@/types";
import { trackUsage } from "@/lib/usage-tracker";
import { useI18n } from "@/lib/i18n";

export default function PracticePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { t, locale } = useI18n();
  const isZh = locale === "zh";
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [generatingAI, setGeneratingAI] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
  const [showExamPrep, setShowExamPrep] = useState(false);
  const [examScope, setExamScope] = useState("");
  const [examPrepLoading, setExamPrepLoading] = useState(false);
  const [examPrepResult, setExamPrepResult] = useState<{ topics_found: number; topics_processed: number; questions_generated: number; topics_failed: string[]; topics: string[] } | null>(null);
  const [examPrepError, setExamPrepError] = useState<string | null>(null);
  const [questionMode, setQuestionMode] = useState<"solving" | "reviewing">("solving");

  useEffect(() => {
    fetch(`/api/questions?courseId=${id}`)
      .then((r) => r.json())
      .then((data) => { setQuestions(data); setLoading(false); });
  }, [id]);

  async function handleExamUpload(result: { storagePath: string }) {
    setGenerating(true);
    const res = await fetch("/api/questions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courseId: id, storagePath: result.storagePath }),
    });
    const newQuestions = await res.json();
    if (res.ok) {
      trackUsage(10000, 3000); // Estimated exam question extraction tokens
      setQuestions((prev) => [...newQuestions, ...prev]);
      setCurrentIndex(0);
      setQuestionMode("solving");
    }
    setGenerating(false);
    setShowUpload(false);
  }

  function handleAnswer() {
    setQuestionMode("reviewing");
  }

  const progress = questions.length > 0 ? ((currentIndex + 1) / questions.length) * 100 : 0;

  if (loading) {
    return (
      <div className="space-y-8">
        <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
          <ArrowLeft size={14} />
          Back to Dashboard
        </Link>
        <CourseTabs courseId={id} />
        <div className="ui-panel p-10 md:p-14 flex flex-col items-center gap-4 text-center">
          <Loader2 className="animate-spin" size={30} style={{ color: "var(--accent)" }} />
          <div>
            <p className="text-lg font-medium">{t("practice.loadingQuestions")}</p>
            <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
              {t("practice.loadingDesc")}
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>
      <CourseTabs courseId={id} />

      <div className="ui-panel p-6 md:p-8 flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
        <div>
          <div className="ui-kicker mb-4">{t("practice.title")}</div>
          <h2 className="text-3xl font-semibold">{t("practice.turnMaterial")}</h2>
          <p className="ui-copy mt-3 max-w-2xl">
            {t("practice.workThrough")}
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => { setShowExamPrep(!showExamPrep); setShowUpload(false); }}
            className="ui-button-primary"
          >
            <Sparkles size={14} />
            {showExamPrep ? (isZh ? "收起" : "Hide Exam Prep") : (isZh ? "考前冲刺" : "Exam Prep")}
          </button>
          <button
            onClick={() => { setShowUpload(!showUpload); setShowExamPrep(false); }}
            className="ui-button-secondary"
          >
            <Upload size={14} />
            {showUpload ? t("practice.uploadExamHide") : t("practice.uploadExam")}
          </button>
        </div>
      </div>

      {showExamPrep && (
        <div className="ui-panel p-6 md:p-8">
          <div className="ui-kicker mb-3">{isZh ? "考前冲刺" : "EXAM PREP"}</div>
          <h3 className="text-xl font-semibold mb-2">{isZh ? "粘贴考试范围" : "Paste your exam scope"}</h3>
          <p className="ui-copy mb-4">{isZh ? "粘贴老师发的考试范围邮件或文档，AI 会根据考点生成针对性练习题。" : "Paste the email or document that describes what the exam covers. AI will generate targeted practice questions."}</p>
          <textarea
            value={examScope}
            onChange={(e) => setExamScope(e.target.value)}
            placeholder={isZh ? "在此粘贴考试范围...\n\n例如：期中考试范围包括 5.3 误差界、5.5 交替级数、6.1 幂级数..." : "Paste exam topics here...\n\nExample: The midterm covers 5.3 Error bounds, 5.5 Alternating series, 6.1 Power series..."}
            className="ui-textarea text-sm mb-4"
            rows={6}
            disabled={examPrepLoading}
          />
          {examPrepError && (
            <div className="rounded-[18px] px-4 py-3 mb-4" style={{ backgroundColor: "rgba(239,68,68,0.08)", border: "1px solid var(--danger)" }}>
              <p className="text-sm font-medium" style={{ color: "var(--danger)" }}>{examPrepError}</p>
            </div>
          )}
          {examPrepResult && (
            <div className="space-y-2 mb-4">
              <div className="rounded-[18px] px-4 py-3" style={{ backgroundColor: "rgba(22, 163, 74, 0.08)", border: "1px solid var(--success)" }}>
                <p className="text-sm font-medium" style={{ color: "var(--success)" }}>
                  {isZh
                    ? `从 ${examPrepResult.topics_processed} 个主题生成了 ${examPrepResult.questions_generated} 道题`
                    : `Generated ${examPrepResult.questions_generated} questions from ${examPrepResult.topics_processed} topics`}
                </p>
                <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
                  {examPrepResult.topics.join(", ")}
                </p>
              </div>
              {examPrepResult.topics_failed.length > 0 && (
                <div className="rounded-[18px] px-4 py-3" style={{ backgroundColor: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.5)" }}>
                  <p className="text-sm font-medium" style={{ color: "var(--warning)" }}>
                    {isZh
                      ? `${examPrepResult.topics_failed.length} 个主题生成失败，可重试`
                      : `${examPrepResult.topics_failed.length} topic${examPrepResult.topics_failed.length > 1 ? "s" : ""} failed — try again`}
                  </p>
                  <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
                    {examPrepResult.topics_failed.join(", ")}
                  </p>
                </div>
              )}
            </div>
          )}
          <button
            onClick={async () => {
              if (!examScope.trim()) return;
              setExamPrepLoading(true);
              setExamPrepResult(null);
              setExamPrepError(null);
              try {
                const res = await fetch(`/api/courses/${id}/exam-prep`, {
                  method: "POST",
                  headers: { "Content-Type": "application/json" },
                  body: JSON.stringify({ scope_text: examScope }),
                });
                if (res.ok) {
                  const result = await res.json();
                  setExamPrepResult({
                    topics_found: result.topics_found,
                    topics_processed: result.topics_processed ?? result.topics_found,
                    questions_generated: result.questions_generated,
                    topics_failed: result.topics_failed ?? [],
                    topics: result.topics,
                  });
                  if (result.questions_generated > 0) {
                    const qRes = await fetch(`/api/questions?courseId=${id}`);
                    const qs = await qRes.json();
                    setQuestions(qs);
                    setCurrentIndex(0);
                  }
                } else {
                  const err = await res.json().catch(() => null);
                  setExamPrepError(err?.error ?? (isZh ? "生成失败，请稍后重试" : "Generation failed. Please try again."));
                }
              } catch {
                setExamPrepError(isZh ? "网络错误或超时，请重试" : "Network error or timeout. Please retry.");
              }
              setExamPrepLoading(false);
            }}
            disabled={examPrepLoading || !examScope.trim()}
            className="ui-button-primary disabled:opacity-50"
          >
            {examPrepLoading ? (
              <><Loader2 size={16} className="animate-spin" /> {isZh ? "正在生成考试题目..." : "Generating exam questions..."}</>
            ) : (
              <><Sparkles size={16} /> {isZh ? "生成考试题目" : "Generate Exam Questions"}</>
            )}
          </button>
        </div>
      )}

      {showUpload && (
        <div>
          {generating ? (
            <div className="ui-panel p-10 flex items-center gap-3 justify-center">
              <Loader2 size={20} className="animate-spin" style={{ color: "var(--accent)" }} />
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{t("practice.converting")}</p>
            </div>
          ) : (
            <FileDropzone onFileUploaded={handleExamUpload} courseId={id} />
          )}
        </div>
      )}

      {questions.length === 0 ? (
        <div className="ui-empty">
          <p className="text-base font-medium mb-2">{t("practice.noQuestions")}</p>
          <p className="text-sm mb-4" style={{ color: "var(--text-secondary)" }}>
            {t("practice.noQuestionsDesc")}
          </p>
          <button
            onClick={async () => {
              setGeneratingAI(true);
              const res = await fetch(`/api/courses/${id}/generate-questions`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
              });
              if (res.ok) {
                const data = await res.json();
                if (data.generated > 0) {
                  const qRes = await fetch(`/api/questions?courseId=${id}`);
                  const qs = await qRes.json();
                  setQuestions(qs);
                  setCurrentIndex(0);
                }
              }
              setGeneratingAI(false);
            }}
            disabled={generatingAI}
            className="ui-button-primary disabled:opacity-50"
          >
            {generatingAI ? (
              <><Loader2 size={16} className="animate-spin" /> Generating questions...</>
            ) : (
              <><Sparkles size={16} /> Generate Practice Questions</>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-5">
          <StudyTrackerPanel
            courseId={id}
            activeMode={questionMode}
            title="Question Time Track"
            description="We estimate whether you are actively solving, reviewing the explanation, or just sitting on the question without interaction."
          />

          <div className="ui-panel p-5 md:p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <p className="text-sm font-medium">
                  Question {currentIndex + 1} of {questions.length}
                </p>
                <div className="ui-progress-track mt-3 max-w-xs">
                  <div className="ui-progress-bar transition-all" style={{ width: `${progress}%` }} />
                </div>
                <p className="text-xs mt-3" style={{ color: "var(--text-secondary)" }}>
                  After you answer, stay on the card to review the explanation, then move with the arrows when you are ready.
                </p>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setCurrentIndex((i) => Math.max(0, i - 1));
                    setQuestionMode("solving");
                  }}
                  disabled={currentIndex === 0}
                  className="ui-icon-button disabled:opacity-30"
                >
                  <ChevronLeft size={16} />
                </button>
                <button
                  onClick={() => {
                    setCurrentIndex((i) => Math.min(questions.length - 1, i + 1));
                    setQuestionMode("solving");
                  }}
                  disabled={currentIndex === questions.length - 1}
                  className="ui-icon-button disabled:opacity-30"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>

          <div>
            <QuestionCard
              key={questions[currentIndex].id}
              question={questions[currentIndex]}
              onAnswer={handleAnswer}
            />
          </div>
        </div>
      )}
    </div>
  );
}
