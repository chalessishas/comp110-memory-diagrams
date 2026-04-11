"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
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

  useEffect(() => {
    fetch("/api/bookmarks")
      .then((r) => {
        if (!r.ok) return [];
        return r.json();
      })
      .then((data) => { setBookmarks(Array.isArray(data) ? data : []); setLoading(false); })
      .catch(() => { setBookmarks([]); setLoading(false); });
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
      <div className="flex items-center gap-3 mb-3">
        <Bookmark size={20} style={{ color: "var(--accent)" }} />
        <h1 className="text-2xl font-semibold tracking-wide">{t("bank.title")}</h1>
      </div>
      <p className="mb-8 text-sm" style={{ color: "var(--text-secondary)" }}>
        {t("bank.subtitle")}
      </p>

      {bookmarks.length === 0 ? (
        <div className="ui-empty">
          <p style={{ color: "var(--text-secondary)" }}>{t("bank.noSaved")}</p>
          <p className="text-sm mt-1 mb-4" style={{ color: "var(--text-secondary)" }}>
            {t("bank.noSavedDesc")}
          </p>
          <Link href="/dashboard" className="ui-button-secondary">
            {t("bank.browseCourses")}
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {bookmarks.map((bm) => (
            <div
              key={bm.id}
              className="ui-panel p-5 group"
            >
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <p className="text-xs mb-2 font-medium" style={{ color: "var(--text-secondary)" }}>
                    {bm.questions.courses?.title || t("bank.unknownCourse")}
                  </p>
                  <p className="text-sm">{bm.questions.stem}</p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="ui-badge">
                      {t(`qtype.${bm.questions.type}`)}
                    </span>
                    <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
                      {t("bank.answer")} {bm.questions.answer}
                    </span>
                  </div>
                  {bm.questions.explanation && (
                    <p className="text-xs mt-3 p-3 rounded-xl" style={{ backgroundColor: "var(--bg-muted)", color: "var(--text-secondary)" }}>
                      {bm.questions.explanation}
                    </p>
                  )}
                </div>
                <button
                  onClick={() => removeBookmark(bm.questions.id)}
                  className="p-1.5 cursor-pointer opacity-100 md:opacity-0 md:group-hover:opacity-100 transition-opacity"
                  title={t("bank.removeFromBank")}
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
