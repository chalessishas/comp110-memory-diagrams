"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { QuestionCard } from "@/components/QuestionCard";
import { FileDropzone } from "@/components/FileDropzone";
import { ChevronLeft, ChevronRight, Loader2, Upload } from "lucide-react";
import type { Question } from "@/types";

export default function PracticePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [showUpload, setShowUpload] = useState(false);

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
      setQuestions((prev) => [...newQuestions, ...prev]);
      setCurrentIndex(0);
    }
    setGenerating(false);
    setShowUpload(false);
  }

  function handleAnswer() {
    setTimeout(() => {
      if (currentIndex < questions.length - 1) setCurrentIndex((i) => i + 1);
    }, 2000);
  }

  if (loading) return <div><CourseTabs courseId={id} /><Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--accent)" }} /></div>;

  return (
    <div>
      <CourseTabs courseId={id} />

      <div className="flex items-center justify-between mb-6">
        <h2 className="text-lg font-medium">Practice</h2>
        <button
          onClick={() => setShowUpload(!showUpload)}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm cursor-pointer"
          style={{ border: "1px solid var(--border)", color: "var(--text-secondary)" }}
        >
          <Upload size={14} />
          Upload Exam
        </button>
      </div>

      {showUpload && (
        <div className="mb-6">
          {generating ? (
            <div className="flex items-center gap-2 py-8 justify-center">
              <Loader2 size={20} className="animate-spin" style={{ color: "var(--accent)" }} />
              <p className="text-sm" style={{ color: "var(--text-secondary)" }}>AI is converting questions...</p>
            </div>
          ) : (
            <FileDropzone onFileUploaded={handleExamUpload} courseId={id} />
          )}
        </div>
      )}

      {questions.length === 0 ? (
        <div className="text-center py-16">
          <p className="mb-2" style={{ color: "var(--text-secondary)" }}>No practice questions yet</p>
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>Upload a past exam or practice sheet to generate interactive questions</p>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-4">
            <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
              Question {currentIndex + 1} of {questions.length}
            </p>
            <div className="flex gap-2">
              <button
                onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
                disabled={currentIndex === 0}
                className="p-1.5 rounded-lg cursor-pointer disabled:opacity-30"
                style={{ border: "1px solid var(--border)" }}
              >
                <ChevronLeft size={16} />
              </button>
              <button
                onClick={() => setCurrentIndex((i) => Math.min(questions.length - 1, i + 1))}
                disabled={currentIndex === questions.length - 1}
                className="p-1.5 rounded-lg cursor-pointer disabled:opacity-30"
                style={{ border: "1px solid var(--border)" }}
              >
                <ChevronRight size={16} />
              </button>
            </div>
          </div>
          <QuestionCard
            key={questions[currentIndex].id}
            question={questions[currentIndex]}
            onAnswer={handleAnswer}
          />
        </div>
      )}
    </div>
  );
}
