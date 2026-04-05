"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { BookOpen, ChevronLeft, ChevronRight, Loader2, Sparkles, CheckCircle2 } from "lucide-react";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";
import type { Lesson } from "@/types";
import { useI18n } from "@/lib/i18n";

export default function LearnPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { t } = useI18n();
  const [lessons, setLessons] = useState<Lesson[]>([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    fetch(`/api/courses/${id}/lessons`)
      .then((r) => r.ok ? r.json() : [])
      .then((data) => {
        setLessons(Array.isArray(data) ? data : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [id]);

  async function handleGenerate() {
    setGenerating(true);
    const res = await fetch(`/api/courses/${id}/lessons`, { method: "POST" });
    if (res.ok) {
      const data = await fetch(`/api/courses/${id}/lessons`).then((r) => r.json());
      setLessons(Array.isArray(data) ? data : []);
    }
    setGenerating(false);
  }

  const lesson = lessons[currentIndex];
  const progress = lessons.length > 0 ? ((currentIndex + 1) / lessons.length) * 100 : 0;

  if (loading) return (
    <div>
      <CourseTabs courseId={id} />
      <Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--accent)" }} />
    </div>
  );

  return (
    <div>
      <CourseTabs courseId={id} />

      {lessons.length === 0 ? (
        <div className="text-center py-16">
          <BookOpen size={40} className="mx-auto mb-4" style={{ color: "var(--border)" }} />
          <h2 className="text-xl font-semibold mb-2">{t("learn.noLessons")}</h2>
          <p className="text-sm mb-6" style={{ color: "var(--text-secondary)" }}>
            {t("learn.generateDesc")}
          </p>
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="inline-flex items-center gap-2 px-6 py-3 rounded-xl font-medium cursor-pointer disabled:opacity-50"
            style={{ backgroundColor: "var(--accent)", color: "white" }}
          >
            {generating ? (
              <><Loader2 size={16} className="animate-spin" /> {t("learn.generating")}</>
            ) : (
              <><Sparkles size={16} /> {t("learn.generateBtn")}</>
            )}
          </button>
          {generating && (
            <p className="text-xs mt-3" style={{ color: "var(--text-secondary)" }}>
              {t("learn.generatingDesc")}
            </p>
          )}
        </div>
      ) : lesson ? (
        <div>
          {/* Progress bar */}
          <div className="flex items-center gap-3 mb-6">
            <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
              <div className="h-full rounded-full transition-all" style={{ width: `${progress}%`, backgroundColor: "var(--accent)" }} />
            </div>
            <span className="text-xs font-medium shrink-0" style={{ color: "var(--text-secondary)" }}>
              {currentIndex + 1} / {lessons.length}
            </span>
          </div>

          {/* Lesson card */}
          <div className="ui-panel p-6 md:p-8 mb-6">
            <div className="ui-kicker mb-4">Lesson {currentIndex + 1}</div>
            <h2 className="text-2xl font-semibold mb-6">{lesson.title}</h2>

            <MarkdownRenderer content={lesson.content} />
          </div>

          {/* Key takeaways */}
          {lesson.key_takeaways && (lesson.key_takeaways as string[]).length > 0 && (
            <div className="ui-panel p-5 mb-6" style={{ backgroundColor: "rgba(91, 108, 240, 0.04)" }}>
              <h4 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <CheckCircle2 size={16} style={{ color: "var(--accent)" }} />
                {t("learn.keyTakeaways")}
              </h4>
              <ul className="space-y-2">
                {(lesson.key_takeaways as string[]).map((t, i) => (
                  <li key={i} className="text-sm flex gap-2">
                    <span style={{ color: "var(--accent)" }}>-</span>
                    <span>{t}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {/* Navigation */}
          <div className="flex items-center justify-between">
            <button
              onClick={() => setCurrentIndex((i) => Math.max(0, i - 1))}
              disabled={currentIndex === 0}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm cursor-pointer disabled:opacity-30"
              style={{ border: "1px solid var(--border)" }}
            >
              <ChevronLeft size={16} /> {t("learn.previous")}
            </button>
            <button
              onClick={() => setCurrentIndex((i) => Math.min(lessons.length - 1, i + 1))}
              disabled={currentIndex === lessons.length - 1}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium cursor-pointer disabled:opacity-30"
              style={{ backgroundColor: "var(--accent)", color: "white" }}
            >
              {t("learn.next")} <ChevronRight size={16} />
            </button>
          </div>
        </div>
      ) : null}
    </div>
  );
}
