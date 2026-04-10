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
import { useI18n } from "@/lib/i18n";

const GENERATION_STEP_DURATIONS = [2000, 3000, 3000, 4000, 3000, 3000, 4000, 4000, 5000, 10000];

type Step = "upload" | "parsing" | "preview";

function GeneratingStatus() {
  const { t } = useI18n();
  const [currentStep, setCurrentStep] = useState(0);
  const [elapsed, setElapsed] = useState(0);

  const steps = [
    { text: t("gen.step1"), duration: GENERATION_STEP_DURATIONS[0] },
    { text: t("gen.step2"), duration: GENERATION_STEP_DURATIONS[1] },
    { text: t("gen.step3"), duration: GENERATION_STEP_DURATIONS[2] },
    { text: t("gen.step4"), duration: GENERATION_STEP_DURATIONS[3] },
    { text: t("gen.step5"), duration: GENERATION_STEP_DURATIONS[4] },
    { text: t("gen.step6"), duration: GENERATION_STEP_DURATIONS[5] },
    { text: t("gen.step7"), duration: GENERATION_STEP_DURATIONS[6] },
    { text: t("gen.step8"), duration: GENERATION_STEP_DURATIONS[7] },
    { text: t("gen.step9"), duration: GENERATION_STEP_DURATIONS[8] },
    { text: t("gen.step10"), duration: GENERATION_STEP_DURATIONS[9] },
  ];

  useEffect(() => {
    const start = Date.now();
    const interval = setInterval(() => {
      const ms = Date.now() - start;
      setElapsed(ms);

      let accumulated = 0;
      for (let i = 0; i < steps.length; i++) {
        accumulated += steps[i].duration;
        if (ms < accumulated) {
          setCurrentStep(i);
          return;
        }
      }
      setCurrentStep(steps.length - 1);
    }, 200);

    return () => clearInterval(interval);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const step = steps[currentStep];
  const totalDuration = steps.reduce((s, st) => s + st.duration, 0);
  const progress = Math.min((elapsed / totalDuration) * 100, 95);

  return (
    <div className="ui-panel p-10 md:p-14 flex flex-col items-center text-center gap-6">
      {/* Spinner */}
      <div className="relative">
        <Loader2 size={36} className="animate-spin" style={{ color: "var(--accent)" }} />
      </div>

      {/* Current step text */}
      <div>
        <p className="text-lg font-medium" style={{ minHeight: "1.8em" }}>{step.text}</p>
        <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
          {Math.floor(elapsed / 1000)}s {t("gen.elapsed")}
        </p>
      </div>

      {/* Progress bar */}
      <div className="w-full max-w-sm">
        <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
          <div
            className="h-full rounded-full"
            style={{
              width: `${progress}%`,
              backgroundColor: "var(--accent)",
              transition: "width 400ms ease",
            }}
          />
        </div>
      </div>

      {/* Timeout warning */}
      {elapsed > 30000 && (
        <p className="text-xs px-4 py-2 rounded-xl" style={{ backgroundColor: "var(--bg-muted)", color: "var(--warning)" }}>
          {t("gen.slowWarning")}
        </p>
      )}

      {/* Step log (like game world gen) */}
      <div className="w-full max-w-sm text-left space-y-1.5 mt-2">
        {steps.slice(0, currentStep + 1).map((s, i) => (
          <div key={i} className="flex items-center gap-2 text-xs" style={{ color: i < currentStep ? "var(--success)" : "var(--text-primary)" }}>
            {i < currentStep ? (
              <Check size={12} style={{ color: "var(--success)" }} />
            ) : (
              <Loader2 size={12} className="animate-spin" style={{ color: "var(--accent)" }} />
            )}
            <span style={{ opacity: i < currentStep ? 0.6 : 1 }}>{s.text}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
function PreviewQuestionCard({ question }: { question: ParsedQuestion & { matched_kp_title: string } }) {
  const { t } = useI18n();
  const [selected, setSelected] = useState<string | null>(null);
  const [textAnswer, setTextAnswer] = useState("");
  const [submitted, setSubmitted] = useState(false);

  const userAnswer = question.type === "multiple_choice" || question.type === "true_false"
    ? selected ?? "" : textAnswer;
  const isCorrect = submitted && userAnswer.trim().toLowerCase() === question.answer.trim().toLowerCase();

  function handleSubmit() {
    if (!userAnswer) return;
    setSubmitted(true);
  }

  return (
    <div className="ui-panel px-5 py-5">
      <div className="flex flex-wrap gap-2 mb-3">
        <span className="ui-badge">{question.type.replaceAll("_", " ")}</span>
        <span className="ui-badge">{question.matched_kp_title}</span>
      </div>
      <p className="text-sm font-medium mb-3">{question.stem}</p>

      {(question.type === "multiple_choice" || question.type === "true_false") && question.options && (
        <div className="space-y-2 mb-3">
          {question.options.map((opt) => (
            <button
              key={opt.label}
              onClick={() => !submitted && setSelected(opt.label)}
              disabled={submitted}
              className="w-full text-left px-4 py-2.5 rounded-xl text-sm cursor-pointer disabled:cursor-default transition-colors"
              style={{
                border: "1px solid",
                borderColor: submitted
                  ? opt.label.toLowerCase() === question.answer.trim().toLowerCase()
                    ? "var(--success)" : selected === opt.label ? "var(--danger)" : "var(--border)"
                  : selected === opt.label ? "var(--accent)" : "var(--border)",
                backgroundColor: submitted
                  ? opt.label.toLowerCase() === question.answer.trim().toLowerCase()
                    ? "var(--bg-muted)" : "transparent"
                  : selected === opt.label ? "var(--accent-light)" : "transparent",
              }}
            >
              <span className="font-medium mr-2">{opt.label}.</span>{opt.text}
            </button>
          ))}
        </div>
      )}

      {(question.type === "fill_blank" || question.type === "short_answer") && (
        <input
          value={textAnswer}
          onChange={(e) => !submitted && setTextAnswer(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSubmit()}
          disabled={submitted}
          placeholder={t("newCourse.answerPlaceholder")}
          className="w-full px-4 py-2.5 rounded-xl text-sm mb-3 outline-none"
          style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-surface)" }}
        />
      )}

      {!submitted ? (
        <button
          onClick={handleSubmit}
          disabled={!userAnswer}
          className="px-5 py-2 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-30"
          style={{ backgroundColor: "var(--accent)", color: "white" }}
        >
          Check
        </button>
      ) : (
        <div className="mt-2">
          <div className="flex items-center gap-2 mb-2">
            {isCorrect ? (
              <><Check size={14} style={{ color: "var(--success)" }} /><span className="text-sm font-medium" style={{ color: "var(--success)" }}>{t("newCourse.correct")}</span></>
            ) : (
              <><span className="text-sm font-medium" style={{ color: "var(--danger)" }}>{t("bank.answer")} {question.answer}</span></>
            )}
          </div>
          {question.explanation && (
            <p className="text-xs p-3 rounded-xl" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
              {question.explanation}
            </p>
          )}
        </div>
      )}
    </div>
  );
}

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
  const { t, locale } = useI18n();
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
      body: JSON.stringify({ storagePath: result.storagePath, parseType: "syllabus", language: locale }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || t("newCourse.failedParseFile"));
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
      body: JSON.stringify({ rawText, parseType: "syllabus", language: locale }),
    });

    const data = await res.json();
    if (!res.ok) {
      setError(data.error || t("newCourse.failedParseText"));
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
      setPreviewError(data.error || t("newCourse.failedPreview"));
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
      setGuestNotice(t("newCourse.guestNotice"));
      return;
    }

    setCreating(true);
    setSaveStage(t("newCourse.savingCourse"));
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
      setError(course.error || t("newCourse.failedCreate"));
      setCreating(false);
      setSaveStage(null);
      return;
    }

    setSaveStage(t("newCourse.savingOutline"));
    const res = await fetch(`/api/courses/${course.id}/outline`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ nodes: parsed.nodes }),
    });

    if (!res.ok) {
      setError(t("newCourse.failedSaveOutline"));
      setCreating(false);
      setSaveStage(null);
      return;
    }

    // Fire-and-forget — don't block navigation waiting for AI generation
    fetch(`/api/courses/${course.id}/generate`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ language: locale }),
    })
      .then(() => trackUsage(15000, 5000))
      .catch(() => {});

    setSaveStage(t("newCourse.redirecting"));
    router.push(`/course/${course.id}`);
  }

  return (
    <div className="max-w-4xl mx-auto py-4 space-y-8">
      <Link href="/dashboard" className="ui-button-ghost w-fit !px-0">
        <ArrowLeft size={14} />
        {t("newCourse.back")}
      </Link>

      <div className="ui-panel p-6 md:p-8">
        <div className="ui-kicker mb-4">{t("newCourse.kicker")}</div>
        <h1 className="text-4xl font-semibold tracking-tight mb-3">{t("newCourse.title")}</h1>
        <p className="ui-copy max-w-2xl">
          {t("newCourse.desc")}
        </p>

        <div className="grid gap-3 mt-6 md:grid-cols-3">
          {[
            { key: "upload", label: t("newCourse.upload") },
            { key: "parsing", label: t("newCourse.analyze") },
            { key: "preview", label: t("newCourse.review") },
          ].map((item) => {
            const isActive = step === item.key;
            return (
              <div
                key={item.key}
                className="rounded-[20px] px-4 py-4"
                style={{
                  backgroundColor: isActive ? "var(--accent-light)" : "var(--bg-muted)",
                }}
              >
                <p className="text-[11px] font-medium uppercase tracking-[0.06em]" style={{ color: isActive ? "var(--accent)" : "var(--text-secondary)" }}>
                  {t("newCourse.step")}
                </p>
                <p className="text-base font-medium mt-2" style={{ color: isActive ? "var(--accent)" : "var(--text-primary)" }}>{item.label}</p>
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
                {t("newCourse.pasteText")}
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
                {t("newCourse.uploadFile")}
              </button>
            </div>
          </div>

          {inputMode === "paste" ? (
            <div className="ui-panel p-5 md:p-6">
              <div className="ui-kicker mb-4">{t("newCourse.textInput")}</div>
              <h2 className="text-2xl font-semibold">{t("newCourse.pasteTitle")}</h2>
              <p className="ui-copy mt-2 max-w-2xl">
                {t("newCourse.pasteDesc")}
              </p>

              <textarea
                value={rawText}
                onChange={(e) => {
                  setRawText(e.target.value);
                  setError(null);
                  setGuestNotice(null);
                }}
                placeholder={t("newCourse.placeholder")}
                className="ui-textarea mt-5 min-h-[280px]"
              />

              <div className="flex flex-col gap-4 mt-5 md:flex-row md:items-center md:justify-between">
                <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                  {rawText.trim().length} {t("newCourse.charCount")}
                </p>
                <button
                  onClick={handleTextParse}
                  disabled={!canParseText}
                  className="ui-button-primary disabled:opacity-40"
                >
                  <Sparkles size={16} />
                  {t("newCourse.generate")}
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
        <GeneratingStatus />
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
              <span className="ui-badge">{parsed.nodes.length} {t("newCourse.topSections")}</span>
            </div>
          </div>

          {/* Missing info warning */}
          {parsed.confidence && parsed.confidence !== "high" && (
            <div className="rounded-[20px] p-5" style={{
              backgroundColor: "var(--bg-muted)",
            }}>
              <p className="text-sm font-medium mb-2" style={{ color: parsed.confidence === "low" ? "var(--danger)" : "var(--warning)" }}>
                {parsed.confidence === "low" ? t("newCourse.missingLow") : t("newCourse.missingMed")}
              </p>
              {parsed.missing_info && parsed.missing_info.length > 0 && (
                <ul className="text-xs space-y-1" style={{ color: "var(--text-secondary)" }}>
                  {parsed.missing_info.map((info, i) => (
                    <li key={i}>- {info}</li>
                  ))}
                </ul>
              )}
              <p className="text-xs mt-3" style={{ color: "var(--text-secondary)" }}>
                {t("newCourse.missingTip")}
              </p>
            </div>
          )}

          <div>
            <div className="ui-kicker mb-3">{t("newCourse.outlinePreview")}</div>
            <h3 className="text-2xl font-semibold mb-2">{t("newCourse.checkMap")}</h3>
            <p className="ui-copy mb-4">
              {isAuthenticated
                ? t("newCourse.authSave")
                : t("newCourse.guestExplore")}
            </p>
          </div>
          <OutlinePreview nodes={parsed.nodes} />

          <div className="grid gap-6 xl:grid-cols-2">
            <div className="ui-panel p-5 md:p-6">
              <div className="flex items-center gap-3 mb-4">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <BookOpen size={18} />
                </div>
                <div>
                  <div className="ui-kicker mb-2">{t("newCourse.studyPreview")}</div>
                  <h4 className="text-xl font-semibold">{t("newCourse.studyPreviewTitle")}</h4>
                </div>
              </div>

              {previewLoading ? (
                <div className="ui-empty">
                  <Loader2 size={22} className="animate-spin mx-auto" style={{ color: "var(--accent)" }} />
                  <p className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
                    {t("newCourse.buildingTasks")}
                  </p>
                </div>
              ) : previewTasks.length > 0 ? (
                <div className="space-y-3">
                  {previewTasks.slice(0, 6).map((task, index) => (
                    <div
                      key={`${task.title}-${index}`}
                      className="rounded-[20px] px-4 py-4"
                      style={{ backgroundColor: "var(--bg-muted)" }}
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
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <BrainCircuit size={18} />
                </div>
                <div>
                  <div className="ui-kicker mb-2">{t("newCourse.tryNow")}</div>
                  <h4 className="text-xl font-semibold">{t("newCourse.answerNoSignup")}</h4>
                </div>
              </div>

              {previewLoading ? (
                <div className="ui-empty">
                  <Loader2 size={22} className="animate-spin mx-auto" style={{ color: "var(--accent)" }} />
                  <p className="text-sm mt-3" style={{ color: "var(--text-secondary)" }}>
                    {t("newCourse.generatingQuestions")}
                  </p>
                </div>
              ) : previewQuestions.length > 0 ? (
                <div className="space-y-3">
                  {previewQuestions.slice(0, 5).map((question, index) => (
                    <PreviewQuestionCard key={`${question.stem}-${index}`} question={question} />
                  ))}
                </div>
              ) : (
                <div className="ui-empty">
                  <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    {t("newCourse.questionPreviewEmpty")}
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
                  <div className="ui-kicker mb-3">{t("newCourse.guestMode")}</div>
                  <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
                    {t("newCourse.guestReady")}
                  </p>
                </div>
                <Link href="/login" target="_blank" rel="noreferrer" className="ui-button-secondary">
                  <LogIn size={16} />
                  {t("newCourse.signInTab")}
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
              {t("newCourse.tryAnother")}
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
                {t("newCourse.loginToSave")}
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
        <div className="ui-panel p-5 flex items-center gap-3">
          <Loader2 size={16} className="animate-spin shrink-0" style={{ color: "var(--accent)" }} />
          <span className="text-sm" style={{ color: "var(--text-secondary)" }}>{saveStage}</span>
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
