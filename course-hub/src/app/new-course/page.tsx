"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { FileDropzone } from "@/components/FileDropzone";
import { OutlinePreview } from "@/components/OutlinePreview";
import { Loader2, Check, ArrowLeft } from "lucide-react";
import Link from "next/link";
import type { ParsedSyllabus } from "@/types";

type Step = "upload" | "parsing" | "preview";

export default function NewCoursePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("upload");
  const [storagePath, setStoragePath] = useState<string | null>(null);
  const [parsed, setParsed] = useState<ParsedSyllabus | null>(null);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleFileUploaded(result: { storagePath: string }) {
    setStoragePath(result.storagePath);
    setStep("parsing");
    setError(null);

    const res = await fetch("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ storagePath: result.storagePath, parseType: "syllabus" }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || "Failed to parse file");
      setStep("upload");
      return;
    }

    setParsed(data.data);
    setStep("preview");
  }

  async function handleCreate() {
    if (!parsed || !storagePath) return;
    setCreating(true);

    const courseRes = await fetch("/api/courses", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        title: parsed.title,
        description: parsed.description,
        professor: parsed.professor,
        semester: parsed.semester,
      }),
    });

    const course = await courseRes.json();
    if (!courseRes.ok) {
      setError(course.error || "Failed to create course");
      setCreating(false);
      return;
    }

    const res = await fetch(`/api/courses/${course.id}/outline`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nodes: parsed.nodes }),
    });

    if (!res.ok) {
      setError("Course created but failed to save outline");
      setCreating(false);
      return;
    }

    router.push(`/course/${course.id}`);
  }

  return (
    <div className="max-w-2xl mx-auto py-8">
      <Link href="/dashboard" className="flex items-center gap-1 text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <h1 className="text-2xl font-semibold mb-2">New Course</h1>
      <p className="mb-8" style={{ color: "var(--text-secondary)" }}>
        Upload your syllabus and AI will create the course structure for you.
      </p>

      {step === "upload" && (
        <FileDropzone onFileUploaded={handleFileUploaded} />
      )}

      {step === "parsing" && (
        <div className="flex flex-col items-center py-16 gap-3">
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent)" }} />
          <p style={{ color: "var(--text-secondary)" }}>AI is reading your syllabus...</p>
        </div>
      )}

      {step === "preview" && parsed && (
        <div>
          <div className="mb-6 p-4 rounded-xl" style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}>
            <h2 className="text-lg font-medium">{parsed.title}</h2>
            <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{parsed.description}</p>
            {parsed.professor && <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>Instructor: {parsed.professor}</p>}
            {parsed.semester && <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>{parsed.semester}</p>}
          </div>

          <h3 className="font-medium mb-3">Course Outline</h3>
          <OutlinePreview nodes={parsed.nodes} />

          <div className="flex gap-3 mt-6">
            <button
              onClick={() => { setStep("upload"); setParsed(null); }}
              className="px-4 py-2 rounded-lg text-sm border cursor-pointer"
              style={{ borderColor: "var(--border)", color: "var(--text-secondary)" }}
            >
              Upload Different File
            </button>
            <button
              onClick={handleCreate}
              disabled={creating}
              className="flex items-center gap-2 px-6 py-2 rounded-lg text-sm font-medium cursor-pointer disabled:opacity-50"
              style={{ backgroundColor: "var(--accent)", color: "white" }}
            >
              {creating ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
              Create Course
            </button>
          </div>
        </div>
      )}

      {error && <p className="text-sm mt-4" style={{ color: "var(--danger)" }}>{error}</p>}
    </div>
  );
}
