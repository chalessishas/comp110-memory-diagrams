"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { ChunkLesson } from "@/components/ChunkLesson";
import { BookOpen, ChevronRight, Loader2, Sparkles } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { levelConfig } from "@/lib/mastery-v2";
import type { Lesson, LessonChunk, MasteryLevelV2 } from "@/types";

interface KnowledgePointItem {
  id: string;
  title: string;
  level: MasteryLevelV2;
  hasLesson: boolean;
  lessonId: string | null;
}

export default function LearnPage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const { t, locale } = useI18n();
  const isZh = locale === "zh";
  const [items, setItems] = useState<KnowledgePointItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [activeLessonId, setActiveLessonId] = useState<string | null>(null);
  const [chunks, setChunks] = useState<LessonChunk[]>([]);
  const [loadingChunks, setLoadingChunks] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    Promise.all([
      fetch(`/api/courses/${id}/lessons`).then(r => r.ok ? r.json() : []),
      fetch(`/api/courses/${id}/mastery`).then(r => r.ok ? r.json() : []),
    ]).then(([lessons, mastery]) => {
      const masteryMap = new Map((mastery as { concept_id: string; current_level: MasteryLevelV2 }[]).map(m => [m.concept_id, m.current_level]));

      const list: KnowledgePointItem[] = (lessons as Lesson[]).map(l => ({
        id: l.knowledge_point_id,
        title: l.title,
        level: masteryMap.get(l.knowledge_point_id) ?? "unseen",
        hasLesson: true,
        lessonId: l.id,
      }));

      setItems(list);
      setLoading(false);
    });
  }, [id]);

  async function openLesson(lessonId: string) {
    setActiveLessonId(lessonId);
    setLoadingChunks(true);

    const res = await fetch(`/api/courses/${id}/lessons/${lessonId}/chunks`);
    if (res.ok) {
      const data = await res.json();
      setChunks(data);
    }
    setLoadingChunks(false);
  }

  async function handleGenerate() {
    setGenerating(true);
    await fetch(`/api/courses/${id}/lessons`, { method: "POST" });
    const res = await fetch(`/api/courses/${id}/lessons`);
    const lessons = res.ok ? await res.json() : [];
    setItems((lessons as Lesson[]).map(l => ({
      id: l.knowledge_point_id,
      title: l.title,
      level: "unseen" as MasteryLevelV2,
      hasLesson: true,
      lessonId: l.id,
    })));
    setGenerating(false);
  }

  if (loading) return (
    <div>
      <CourseTabs courseId={id} />
      <Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--accent)" }} />
    </div>
  );

  if (activeLessonId) {
    if (loadingChunks) {
      return (
        <div>
          <CourseTabs courseId={id} />
          <Loader2 className="animate-spin mx-auto mt-16" style={{ color: "var(--accent)" }} />
        </div>
      );
    }

    return (
      <div>
        <CourseTabs courseId={id} />
        <button
          onClick={() => { setActiveLessonId(null); setChunks([]); }}
          className="ui-button-ghost mb-4 !px-0"
        >
          ← {isZh ? "返回知识点列表" : "Back to topics"}
        </button>
        <ChunkLesson chunks={chunks} courseId={id} lessonId={activeLessonId} />
      </div>
    );
  }

  return (
    <div>
      <CourseTabs courseId={id} />

      <div className="flex items-center justify-between mb-6">
        <div>
          <h2 className="text-xl font-semibold">{t("tabs.learn")}</h2>
          <p className="text-sm mt-1" style={{ color: "var(--text-secondary)" }}>
            {isZh ? "选择一个知识点开始学习" : "Pick a topic to start learning"}
          </p>
        </div>
        {items.length === 0 && (
          <button
            onClick={handleGenerate}
            disabled={generating}
            className="ui-button-primary disabled:opacity-50"
          >
            {generating ? <Loader2 size={15} className="animate-spin" /> : <Sparkles size={15} />}
            {isZh ? "生成课程" : "Generate Lessons"}
          </button>
        )}
      </div>

      {items.length === 0 ? (
        <div className="ui-empty">
          <BookOpen size={32} className="mx-auto mb-3" style={{ color: "var(--border)" }} />
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {isZh ? "还没有课程内容。点击上方按钮生成。" : "No lessons yet. Click Generate above."}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item, i) => {
            const config = levelConfig[item.level];
            return (
              <button
                key={item.id}
                onClick={() => item.lessonId && openLesson(item.lessonId)}
                className="w-full ui-panel p-4 flex items-center gap-4 text-left cursor-pointer group"
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold"
                  style={{ backgroundColor: config.bgColor, color: config.color, border: `1px solid ${config.color}20` }}
                >
                  {i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                    {isZh ? config.labelZh : config.label}
                  </p>
                </div>
                <ChevronRight size={16} className="shrink-0 opacity-30 group-hover:opacity-100 transition-opacity" style={{ color: "var(--text-secondary)" }} />
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
