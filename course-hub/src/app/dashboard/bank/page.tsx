"use client";

import { useEffect, useState } from "react";
import { Bookmark, Loader2, Trash2 } from "lucide-react";
import type { QuestionWithAnswer } from "@/types";
import { useI18n } from "@/lib/i18n";

interface BookmarkItem {
  id: string;
  note: string | null;
  created_at: string;
  questions: QuestionWithAnswer & { courses: { title: string } };
}

export default function QuestionBankPage() {
  const { t } = useI18n();
  const [bookmarks, setBookmarks] = useState<BookmarkItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetch("/api/bookmarks")
      .then((r) => {
        if (!r.ok) throw new Error(`Failed to load bookmarks (${r.status})`);
        return r.json();
      })
      .then((data) => { setBookmarks(Array.isArray(data) ? data : []); setLoading(false); })
      .catch((err) => { setError(err.message); setLoading(false); });
  }, []);

  async function removeBookmark(questionId: string) {
    await fetch("/api/bookmarks", {
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question_id: questionId }),
    });
    setBookmarks((prev) => prev.filter((b) => b.questions.id !== questionId));
  }

  if (loading) return (
    <div className="p-8">
      <Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--text-secondary)" }} />
    </div>
  );

  return (
    <div>
      <div className="flex items-center gap-2 mb-6">
        <Bookmark size={20} style={{ color: "var(--accent)" }} />
        <h1 className="text-2xl font-semibold">{t("bank.title")}</h1>
      </div>
      <p className="mb-6 text-sm" style={{ color: "var(--text-secondary)" }}>
        {t("bank.subtitle")}
      </p>

      {error ? (
        <div className="text-center py-16">
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>{error}</p>
          <button onClick={() => window.location.reload()} className="ui-button-secondary mt-3 text-sm">
            {t("bank.retry") || "Retry"}
          </button>
        </div>
      ) : bookmarks.length === 0 ? (
        <div className="text-center py-16">
          <p style={{ color: "var(--text-secondary)" }}>{t("bank.noSaved")}</p>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            {t("bank.noSavedDesc")}
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {bookmarks.map((bm) => (
            <div
              key={bm.id}
              className="p-5 rounded-md group"
              style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-xs mb-2 font-medium" style={{ color: "var(--text-secondary)" }}>
                    {bm.questions.courses?.title || "Unknown course"}
                  </p>
                  <p className="text-sm">{bm.questions.stem}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded-full" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
                      {bm.questions.type.replace("_", " ")}
                    </span>
                    <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                      {t("bank.answer")} {bm.questions.answer}
                    </span>
                  </div>
                  {bm.questions.explanation && (
                    <p className="text-xs mt-2 p-2 rounded-lg" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
                      {bm.questions.explanation}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => removeBookmark(bm.questions.id)}
                  className="p-1.5 cursor-pointer opacity-0 group-hover:opacity-100"
                  title="Remove"
                >
                  <Trash2 size={14} style={{ color: "var(--danger)" }} />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
