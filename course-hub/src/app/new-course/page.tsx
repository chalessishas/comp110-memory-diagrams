"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { createClient } from "@/lib/supabase/client";
import { FileDropzone } from "@/components/FileDropzone";
import { OutlinePreview } from "@/components/OutlinePreview";
import { Loader2, Check, ArrowLeft, ClipboardPenLine, Upload, LogIn, Sparkles, BookOpen, BrainCircuit } from "lucide-react";
import Link from "next/link";
import type { ParsedQuestion, ParsedSyllabus, TaskType } from "@/types";
import { trackUsage } from "@/lib/usage-tracker";

type Step = "upload" | "parsing" | "preview";
type InputMode = "paste" | "upload";
type AuthState = "loading" | "guest" | "authenticated";
type PreviewStudyTask = {
  knowledge_point_title: string;
  title: string;
  description: string;
  task_type: TaskType;
  priority: number;
};
type PreviewQuestion = ParsedQuestion & { matched_kp_title: string };

export default function NewCoursePage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("upload");
  const [inputMode, setInputMode] = useState<InputMode>("paste");
  const [authState, setAuthState] = useState<AuthState>("loading");
  const [parsed, setParsed] = useState<ParsedSyllabus | null>(null);
  const [rawText, setRawText] = useState("");
  const [creating, setCreating] = useState(false);
  const [saveStage, setSaveStage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [guestNotice, setGuestNotice] = useState<string | null>(null);
  const [previewTasks, setPreviewTasks] = useState<PreviewStudyTask[]>([]);
  const [previewQuestions, setPreviewQuestions] = useState<PreviewQuestion[]>([]);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewError, setPreviewError] = useState<string | null>(null);

  const isAuthenticated = authState === "authenticated";
  const canParseText = rawText.trim().length >= 80;

  useEffect(() => {
    let isActive = true;
    const supabase = createClient();

    void supabase.auth.getUser().then(({ data: { user } }) => {
      if (!isActive) return;
      setAuthState(user ? "authenticated" : "guest");
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      if (!isActive) return;
      setAuthState(session?.user ? "authenticated" : "guest");
    });

    return () => {
      isActive = false;
      subscription.unsubscribe();
    };
  }, []);

  async function handleFileUploaded(result: { storagePath: string }) {
    setStep("parsing");
    setError(null);
    setGuestNotice(null);
    setPreviewError(null);
    setPreviewTasks([]);
    setPreviewQuestions([]);

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

    trackUsage(20000, 2000); // Estimated syllabus parse tokens
    setParsed(data.data);
    setStep("preview");
    void loadLearningPreview(data.data);
  }

  async function handleTextParse() {
    if (!canParseText) return;

    setStep("parsing");
    setError(null);
    setGuestNotice(null);
    setPreviewError(null);
    setPreviewTasks([]);
    setPreviewQuestions([]);

    const res = await fetch("/api/parse", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ rawText, parseType: "syllabus" }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || "Failed to parse text");
      setStep("upload");
      return;
    }

    trackUsage(20000, 2000); // Estimated syllabus parse tokens
    setParsed(data.data);
    setStep("preview");
    void loadLearningPreview(data.data);
  }

  async function loadLearningPreview(parsedSyllabus: ParsedSyllabus) {
    setPreviewLoading(true);
    setPreviewError(null);

    const res = await fetch("/api/preview/learning", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ title: parsedSyllabus.title, nodes: parsedSyllabus.nodes }),
    });

    const data = await res.json();
    if (!res.ok) {
      setPreviewError(data.error || "Failed to generate study preview");
      setPreviewLoading(false);
      return;
    }

    setPreviewTasks(data.tasks ?? []);
    setPreviewQuestions(data.questions ?? []);
    setPreviewLoading(false);
  }

  async function handleCreate() {
    if (!parsed) return;

    if (!isAuthenticated) {
      setGuestNotice("You're in guest mode. Sign in when you want to save this course to your dashboard.");
      return;
    }

    setCreating(true);
    setSaveStage("Saving your course...");
    setError(null);
    setGuestNotice(null);

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
      setSaveStage(null);
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
      setSaveStage(null);
      return;
    }

    setSaveStage("Generating study tasks and practice questions...");
    await fetch(`/api/courses/${course.id}/generate`, { method: "POST" });
    trackUsage(15000, 5000); // Estimated study tasks + questions generation tokens

    router.push(`/course/${course.id}`);
  }

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        Back to Dashboard
      </Link>

      <div className="ui-panel p-6 md:p-8">
        <div className="ui-kicker mb-4">New Course</div>
        <h1 className="text-4xl font-semibold tracking-tight mb-3">Build a course from one file.</h1>
        <p className="ui-copy max-w-2xl">
          Upload a file or paste your syllabus text. AI handles the rest.
        </p>

        <div className="grid gap-3 mt-6 md:grid-cols-3">
          {[
            { key: "upload", label: "Upload" },
            { key: "parsing", label: "Analyze" },
            { key: "preview", label: "Review" },
          ].map((item) => {
            const isActive = step === item.key;
            return (
              <div
                key={item.key}
                className="rounded-[22px] px-4 py-4"
                style={{
                  border: `1px solid ${isActive ? "var(--accent)" : "var(--border)"}`,
                  backgroundColor: isActive ? "rgba(16, 16, 16, 0.05)" : "rgba(247, 247, 244, 0.9)",
                }}
              >
                <p className="text-[11px] font-semibold uppercase tracking-[0.24em]" style={{ color: "var(--text-secondary)" }}>
                  Step
                </p>
                <p className="text-base font-medium mt-2">{item.label}</p>
              </div>
            );
          })}
        </div>
      </div>

      {step === "upload" && (
        <div className="space-y-6">
          <div className="ui-panel p-5 md:p-6">
            <div className="ui-segmented">
              <button
                type="button"
                onClick={() => {
                  setInputMode("paste");
                  setError(null);
                  setGuestNotice(null);
                }}
                className={`ui-segment ${inputMode === "paste" ? "ui-segment-active" : ""}`}
              >
                <ClipboardPenLine size={16} />
                Paste Text
              </button>
              <button
                type="button"
                onClick={() => {
                  setInputMode("upload");
                  setError(null);
                  setGuestNotice(null);
                }}
                className={`ui-segment ${inputMode === "upload" ? "ui-segment-active" : ""}`}
              >
                <Upload size={16} />
                Upload File
              </button>
            </div>
          </div>

          {inputMode === "paste" ? (
            <div className="ui-panel p-5 md:p-6">
              <div className="ui-kicker mb-4">Text Input</div>
              <h2 className="text-2xl font-semibold">Paste a syllabus, course plan, or class overview.</h2>
              <p className="ui-copy mt-2 max-w-2xl">
                Works without an account. Paste any course text and see the outline AI generates.
              </p>

              <textarea
                value={rawText}
                onChange={(e) => {
                  setRawText(e.target.value);
                  setError(null);
                  setGuestNotice(null);
                }}
                placeholder={`Example:\nCourse: Introduction to Cognitive Science\nInstructor: Dr. Lee\nWeeks 1-2: Foundations of perception\nWeek 3: Memory systems\nWeek 4: Language processing...`}
                className="ui-textarea mt-5 min-h-[280px]"
              />

              <div className="flex flex-col gap-4 mt-5 md:flex-row md:items-center md:justify-between">
                <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                  {rawText.trim().length} characters. Paste at least a short syllabus or course outline to continue.
                </p>
                <button
                  onClick={handleTextParse}
                  disabled={!canParseText}
                  className="ui-button-primary disabled:opacity-40"
                >
                  <Sparkles size={16} />
                  Generate Preview
                </button>
              </div>
            </div>
          ) : isAuthenticated ? (
            <FileDropzone onFileUploaded={handleFileUploaded} />
          ) : authState === "loading" ? (
            <div className="ui-panel p-8 text-center">
              <Loader2 size={24} className="animate-spin mx-auto" style={{ color: "var(--accent)" }} />
              <p className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
                Checking your session...
              </p>
            </div>
          ) : (
            <div className="ui-panel p-6 md:p-8">
              <div className="ui-kicker mb-4">Login For Uploads</div>
              <h2 className="text-2xl font-semibold">Guests can paste text right away.</h2>
              <p className="ui-copy mt-2 max-w-2xl">
                File uploads still depend on your account because the file is stored before parsing. If you only want to try the product, use the paste tab first.
              </p>
              <div className="flex flex-wrap gap-3 mt-5">
                <button
                  type="button"
                  onClick={() => setInputMode("paste")}
                  className="ui-button-secondary"
                >
                  <ClipboardPenLine size={16} />
                  Switch to Paste
                </button>
                <Link href="/login" className="ui-button-primary">
                  <LogIn size={16} />
                  Sign In to Upload
                </Link>
              </div>
            </div>
          )}
        </div>
      )}

      {step === "parsing" && (
        <div className="ui-panel p-10 md:p-14 flex flex-col items-center text-center gap-4">
          <Loader2 size={32} className="animate-spin" style={{ color: "var(--accent)" }} />
          <div>
            <p className="text-lg font-medium">Reading your syllabus...</p>
            <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
              CourseHub is extracting the structure, topics, and likely knowledge points.
            </p>
          </div>
        </div>
      )}

      {step === "preview" && parsed && (
        <div className="space-y-6">
          <div className="ui-panel p-6 md:p-8">
            <div className="ui-kicker mb-4">Preview</div>
            <h2 className="text-3xl font-semibold">{parsed.title}</h2>
            <p className="text-sm mt-3 max-w-2xl" style={{ color: "var(--text-secondary)" }}>{parsed.description}</p>
            <div className="flex flex-wrap gap-2 mt-5">
              {parsed.professor && <span className="ui-badge">Instructor: {parsed.professor}</span>}
              {parsed.semester && <span className="ui-badge">{parsed.semester}</span>}
              <span className="ui-badge">{parsed.nodes.length} top-level sections</span>
            </div>
          </div>

          <div>
            <div className="ui-kicker mb-3">Outline Preview</div>
            <h3 className="text-2xl font-semibold mb-2">Check the course map before creating it.</h3>
            <p className="ui-copy mb-4">
              {isAuthenticated
                ? "If this looks right, CourseHub will save it and generate supporting study materials."
                : "You can keep exploring in guest mode. Sign in only when you're ready to save this preview to your dashboard."}
            </p>
          </div>
          <OutlinePreview nodes={parsed.nodes} />

          <div className="grid gap-6 xl:grid-cols-2">
            <div className="ui-panel p-5 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
                  <BookOpen size={18} />
                </div>
                <div>
                  <div className="ui-kicker mb-2">Study Preview</div>
                  <h4 className="text-xl font-semibold">What would this course ask you to do?</h4>
                </div>
              </div>

              {previewLoading ? (
                <div className="ui-empty">
                  <Loader2 size={22} className="animate-spin mx-auto" style={{ color: "var(--accent)" }} />
                  <p className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
                    Building study tasks from the outline...
                  </p>
                </div>
              ) : previewTasks.length > 0 ? (
                <div className="space-y-3">
                  {previewTasks.slice(0, 6).map((task, index) => (
                    <div
                      key={`${task.title}-${index}`}
                      className="rounded-[22px] px-4 py-4"
                      style={{ border: "1px solid var(--border)", backgroundColor: "rgba(247, 247, 244, 0.92)" }}
                    >
                      <div className="flex items-center justify-between gap-3">
                        <p className="text-sm font-medium">{task.title}</p>
                        <span className="ui-badge">{task.task_type}</span>
                      </div>
                      <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
                        {task.description}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="ui-empty">
                  <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    Study-task preview is not ready yet.
                  </p>
                </div>
              )}
            </div>

            <div className="ui-panel p-5 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl" style={{ backgroundColor: "var(--bg-muted)", border: "1px solid var(--border)" }}>
                  <BrainCircuit size={18} />
                </div>
                <div>
                  <div className="ui-kicker mb-2">Question Preview</div>
                  <h4 className="text-xl font-semibold">What kind of practice would it generate?</h4>
                </div>
              </div>

              {previewLoading ? (
                <div className="ui-empty">
                  <Loader2 size={22} className="animate-spin mx-auto" style={{ color: "var(--accent)" }} />
                  <p className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
                    Generating sample questions...
                  </p>
                </div>
              ) : previewQuestions.length > 0 ? (
                <div className="space-y-3">
                  {previewQuestions.slice(0, 3).map((question, index) => (
                    <div
                      key={`${question.stem}-${index}`}
                      className="rounded-[22px] px-4 py-4"
                      style={{ border: "1px solid var(--border)", backgroundColor: "white" }}
                    >
                      <div className="flex flex-wrap gap-2 mb-3">
                        <span className="ui-badge">{question.type.replaceAll("_", " ")}</span>
                        <span className="ui-badge">{question.matched_kp_title}</span>
                      </div>
                      <p className="text-sm font-medium">{question.stem}</p>
                      {question.options && question.options.length > 0 && (
                        <div className="mt-3 space-y-2">
                          {question.options.map((option) => (
                            <div
                              key={`${question.stem}-${option.label}`}
                              className="rounded-2xl px-3 py-2 text-sm"
                              style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-muted)" }}
                            >
                              <span className="font-medium mr-2">{option.label}.</span>
                              {option.text}
                            </div>
                          ))}
                        </div>
                      )}
                      <p className="text-xs mt-3" style={{ color: "var(--text-secondary)" }}>
                        Answer: {question.answer}
                      </p>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="ui-empty">
                  <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    Question preview is not ready yet.
                  </p>
                </div>
              )}
            </div>
          </div>

          {previewError && (
            <div className="ui-panel ui-panel-muted p-4 text-sm" style={{ color: "var(--danger)" }}>
              {previewError}
            </div>
          )}

          {!isAuthenticated && (
            <div className="ui-panel ui-panel-muted p-5">
              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                <div>
                  <div className="ui-kicker mb-3">Guest Mode</div>
                  <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    Your preview is ready. Open sign in in another tab whenever you want to save it permanently.
                  </p>
                </div>
                <Link href="/login" target="_blank" rel="noreferrer" className="ui-button-secondary">
                  <LogIn size={16} />
                  Sign In in Another Tab
                </Link>
              </div>
            </div>
          )}

          <div className="flex flex-wrap gap-3">
            <button
              onClick={() => {
                setStep("upload");
                setParsed(null);
                setError(null);
                setGuestNotice(null);
              }}
              className="ui-button-secondary"
            >
              Try Another Input
            </button>
            {isAuthenticated ? (
              <button
                onClick={handleCreate}
                disabled={creating}
                className="ui-button-primary disabled:opacity-50"
              >
                {creating ? <Loader2 size={16} className="animate-spin" /> : <Check size={16} />}
                Save Course to Dashboard
              </button>
            ) : (
              <button
                onClick={handleCreate}
                className="ui-button-primary"
              >
                <LogIn size={16} />
                Log In to Save
              </button>
            )}
          </div>
        </div>
      )}

      {guestNotice && (
        <div className="ui-panel ui-panel-muted p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          {guestNotice}
        </div>
      )}

      {creating && saveStage && (
        <div className="ui-panel p-4 text-sm" style={{ color: "var(--text-secondary)" }}>
          {saveStage}
        </div>
      )}

      {error && (
        <div className="ui-panel ui-panel-muted p-4 text-sm" style={{ color: "var(--danger)" }}>
          {error}
        </div>
      )}
    </div>
  );
}
