"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { FileDropzone } from "@/components/FileDropzone";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { ChevronLeft, ChevronRight, Loader2, Upload, ArrowLeft, Sparkles, Target, Flag } from "lucide-react";
import type { Question } from "@/types";
import { trackUsage } from "@/lib/usage-tracker";
import { useI18n } from "@/lib/i18n";
import { getExamScope, pullCardsFromServer } from "@/lib/spaced-repetition";
import { SessionSummaryModal } from "@/components/SessionSummaryModal";

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
  const [sessionAnswered, setSessionAnswered] = useState(0);
  const [sessionCorrect, setSessionCorrect] = useState(0);
  const [examScope, setExamScope] = useState("");
  const [examPrepLoading, setExamPrepLoading] = useState(false);
  const [examPrepResult, setExamPrepResult] = useState<{ topics_found: number; topics_processed: number; questions_generated: number; topics_failed: string[]; topics: string[] } | null>(null);
  const [examPrepError, setExamPrepError] = useState<string | null>(null);
  const [questionMode, setQuestionMode] = useState<"solving" | "reviewing">("solving");
  const [scopeKpIds, setScopeKpIds] = useState<Set<string> | null>(null);
  const [showSummary, setShowSummary] = useState(false);
  const [sessionStart] = useState(() => Date.now());
  const [sessionItems, setSessionItems] = useState<{ id: string; stem: string; correct: boolean }[]>([]);

  useEffect(() => {
    const scope = getExamScope(id);
    if (scope && scope.length > 0) setScopeKpIds(new Set(scope));

    // Pull server FSRS state so adaptive sort uses current cross-device history
    pullCardsFromServer(id);

    fetch(`/api/questions?courseId=${id}`)
      .then((r) => r.ok ? r.json() : [])
      .then((data) => { setQuestions(Array.isArray(data) ? data : []); setLoading(false); });
  }, [id]);

  // Filter by exam scope if active
  const filteredQuestions = scopeKpIds
    ? questions.filter((q) => q.knowledge_point_id && scopeKpIds.has(q.knowledge_point_id))
    : questions;

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

  function handleAnswer(questionId: string, _answer: string, isCorrect: boolean) {
    setQuestionMode("reviewing");
    setSessionAnswered((n) => n + 1);
    if (isCorrect) setSessionCorrect((n) => n + 1);
    const q = filteredQuestions.find((q) => q.id === questionId);
    if (q) setSessionItems((prev) => [...prev, { id: questionId, stem: q.stem, correct: isCorrect }]);
  }

  const progress = filteredQuestions.length > 0 ? ((currentIndex + 1) / filteredQuestions.length) * 100 : 0;

  if (loading) {
    return (
      <div className="space-y-8">
        <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
          <ArrowLeft size={14} />
          {t("misc.backToDashboard")}
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
        {t("misc.backToDashboard")}
      </Link>
      <CourseTabs courseId={id} />

      {scopeKpIds && (
        <div className="mb-4 px-4 py-3 rounded-xl flex items-center justify-between" style={{ backgroundColor: "var(--bg-muted)" }}>
          <div className="flex items-center gap-2">
            <Target size={16} style={{ color: "var(--accent)" }} />
            <span className="text-sm font-medium" style={{ color: "var(--accent)" }}>
              {isZh
                ? `考试范围 · ${filteredQuestions.length} 题`
                : `Exam Scope · ${filteredQuestions.length} question${filteredQuestions.length !== 1 ? "s" : ""}`}
            </span>
          </div>
          <button onClick={() => setScopeKpIds(null)} className="text-xs cursor-pointer" style={{ color: "var(--text-muted)" }}>
            {t("practice.showAll")}
          </button>
        </div>
      )}

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
            {showExamPrep ? t("practice.examPrepHide") : t("practice.examPrep")}
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
          <div className="ui-kicker mb-3">{t("practice.examPrepKicker")}</div>
          <h3 className="text-xl font-semibold mb-2">{t("practice.examPrepTitle")}</h3>
          <p className="ui-copy mb-4">{t("practice.examPrepDesc")}</p>
          <textarea
            value={examScope}
            onChange={(e) => setExamScope(e.target.value)}
            placeholder={t("practice.examPrepPlaceholder")}
            className="ui-textarea text-sm mb-4"
            rows={6}
            disabled={examPrepLoading}
          />
          {examPrepError && (
            <div className="rounded-[20px] px-4 py-3 mb-4" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-sm font-medium" style={{ color: "var(--danger)" }}>{examPrepError}</p>
            </div>
          )}
          {examPrepResult && (
            <div className="space-y-2 mb-4">
              <div className="rounded-[20px] px-4 py-3" style={{ backgroundColor: "var(--bg-muted)" }}>
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
                <div className="rounded-[20px] px-4 py-3" style={{ backgroundColor: "var(--bg-muted)" }}>
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
                  setExamPrepError(err?.error ?? t("practice.examPrepFailed"));
                }
              } catch {
                setExamPrepError(t("practice.examPrepTimeout"));
              }
              setExamPrepLoading(false);
            }}
            disabled={examPrepLoading || !examScope.trim()}
            className="ui-button-primary disabled:opacity-50"
          >
            {examPrepLoading ? (
              <><Loader2 size={16} className="animate-spin" /> {t("practice.examPrepGenerating")}</>
            ) : (
              <><Sparkles size={16} /> {t("practice.examPrepGenerate")}</>
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

      {filteredQuestions.length === 0 ? (
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
              <><Loader2 size={16} className="animate-spin" /> {t("practice.generating")}</>
            ) : (
              <><Sparkles size={16} /> {t("practice.generateBtn")}</>
            )}
          </button>
        </div>
      ) : (
        <div className="space-y-5">
          <StudyTrackerPanel
            courseId={id}
            activeMode={questionMode}
          />

          <div className="ui-panel p-5 md:p-6">
            <div className="flex flex-col gap-4 md:flex-row md:items-end md:justify-between">
              <div>
                <div className="flex items-center gap-3 flex-wrap">
                  <p className="text-sm font-medium">
                    {t("practice.questionOf")} {currentIndex + 1} {t("practice.of")} {filteredQuestions.length}
                  </p>
                  {sessionAnswered >= 3 && (() => {
                    const acc = sessionCorrect / sessionAnswered;
                    const pct = Math.round(acc * 100);
                    const color = acc >= 0.75 && acc <= 0.92
                      ? "var(--success)"
                      : acc > 0.92
                      ? "var(--accent)"
                      : "var(--warning)";
                    return (
                      <span className="text-xs px-2 py-0.5 rounded-lg font-medium" style={{ backgroundColor: "var(--bg-muted)", color }}>
                        {pct}% {t("practice.accuracy")} · {t("practice.target85")}
                      </span>
                    );
                  })()}
                </div>
                <div className="ui-progress-track mt-3 max-w-xs">
                  <div className="ui-progress-bar transition-all" style={{ width: `${progress}%` }} />
                </div>
                <p className="text-xs mt-3" style={{ color: "var(--text-secondary)" }}>
                  {t("practice.reviewHint")}
                </p>
              </div>
              <div className="flex gap-2">
                {sessionAnswered >= 5 && (
                  <button
                    onClick={() => setShowSummary(true)}
                    className="ui-icon-button"
                    title={t("practice.endSession")}
                  >
                    <Flag size={16} />
                  </button>
                )}
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
                    setCurrentIndex((i) => Math.min(filteredQuestions.length - 1, i + 1));
                    setQuestionMode("solving");
                  }}
                  disabled={currentIndex === filteredQuestions.length - 1}
                  className="ui-icon-button disabled:opacity-30"
                >
                  <ChevronRight size={16} />
                </button>
              </div>
            </div>
          </div>

          <div>
            <QuestionCard
              key={filteredQuestions[currentIndex].id}
              question={filteredQuestions[currentIndex]}
              onAnswer={handleAnswer}
            />
          </div>
        </div>
      )}

      <SessionSummaryModal
        open={showSummary}
        onClose={() => setShowSummary(false)}
        courseId={id}
        sessionAnswered={sessionAnswered}
        sessionCorrect={sessionCorrect}
        sessionMinutes={Math.round((Date.now() - sessionStart) / 60_000)}
        sessionStart={sessionStart}
        reviewedItems={sessionItems}
      />
    </div>
  );
}
