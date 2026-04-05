"use client";

import { useEffect, useState, use } from "react";
import Link from "next/link";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { FileDropzone } from "@/components/FileDropzone";
import { StudyTrackerPanel } from "@/components/StudyTrackerPanel";
import { ChevronLeft, ChevronRight, Loader2, Upload, ArrowLeft } from "lucide-react";
import type { Question } from "@/types";
import { trackUsage } from "@/lib/usage-tracker";

export default function PracticePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showUpload, setShowUpload] = useState(false);
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
            <p className="text-lg font-medium">Loading practice questions...</p>
            <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
              Pulling together the current practice set for this course.
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
          <div className="ui-kicker mb-4">Practice</div>
          <h2 className="text-3xl font-semibold">Turn material into reps.</h2>
          <p className="ui-copy mt-3 max-w-2xl">
            Work through generated questions or upload an exam to build a fresh drill set.
          </p>
        </div>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="ui-button-secondary"
        >
          <Upload size={14} />
          {showUpload ? "Hide Upload" : "Upload Exam"}
        </button>
      </div>

      {showUpload && (
        <div>
          {generating ? (
            <div className="ui-panel p-10 flex items-center gap-3 justify-center">
              <Loader2 size={20} className="animate-spin" style={{ color: "var(--accent)" }} />
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>AI is converting questions...</p>
            </div>
          ) : (
            <FileDropzone onFileUploaded={handleExamUpload} courseId={id} />
          )}
        </div>
      )}

      {questions.length === 0 ? (
        <div className="ui-empty">
          <p className="text-base font-medium mb-2">No practice questions yet</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            Upload a past exam or practice sheet to generate interactive questions.
          </p>
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
