"use client";

import { useState } from "react";
import { BookOpen, Loader2, CheckCircle2, AlertCircle, MinusCircle } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface Props {
  courseId: string;
  questionId: string;
}

export function TeachBackPanel({ courseId, questionId }: Props) {
  const { t } = useI18n();
  const [expanded, setExpanded] = useState(false);
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ feedback: string; quality: "strong" | "partial" | "missing" } | null>(null);

  async function handleSubmit() {
    if (!text.trim() || loading) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/courses/${courseId}/teach-back`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question_id: questionId,
          user_explanation: text,
        }),
      });
      const data = await res.json();
      if (data.feedback) setResult(data);
    } catch { /* ignore */ }
    setLoading(false);
  }

  const qualityConfig = {
    strong:  { icon: CheckCircle2, color: "var(--success)",  label: t("teachBack.strong") },
    partial: { icon: AlertCircle,  color: "var(--warning)",  label: t("teachBack.partial") },
    missing: { icon: MinusCircle,  color: "var(--danger)",   label: t("teachBack.missing") },
  };
  const q = result ? qualityConfig[result.quality] : null;

  return (
    <div className="mt-3 rounded-[20px] overflow-hidden" style={{ backgroundColor: "var(--bg-muted)" }}>
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-2 px-5 py-3 text-left cursor-pointer"
        style={{ color: "var(--text-secondary)" }}
      >
        <BookOpen size={14} />
        <span className="text-sm">
          {t("teachBack.explain")}
        </span>
        <span className="ml-auto text-xs" style={{ color: "var(--text-muted)" }}>
          {expanded ? "▲" : "▼"}
        </span>
      </button>

      {expanded && (
        <div className="px-5 pb-5 space-y-3">
          {!result ? (
            <>
              <textarea
                value={text}
                onChange={(e) => setText(e.target.value)}
                placeholder={t("teachBack.placeholder")}
                className="w-full px-3 py-2 rounded-xl text-sm resize-none"
                style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)", minHeight: "72px" }}
              />
              <button
                onClick={handleSubmit}
                disabled={loading || !text.trim()}
                className="ui-button-primary disabled:opacity-30 text-sm"
              >
                {loading ? <Loader2 size={14} className="animate-spin" /> : null}
                {t("teachBack.getFeedback")}
              </button>
            </>
          ) : (
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                {q && <q.icon size={16} style={{ color: q.color }} />}
                <span className="text-xs font-medium" style={{ color: q?.color }}>
                  {q?.label}
                </span>
              </div>
              <p className="text-sm leading-relaxed" style={{ color: "var(--text-primary)" }}>
                {result.feedback}
              </p>
              <button
                onClick={() => { setResult(null); setText(""); }}
                className="text-xs cursor-pointer"
                style={{ color: "var(--text-muted)" }}
              >
                {t("teachBack.tryAgain")}
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
