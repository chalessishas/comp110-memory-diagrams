"use client";

import { useEffect, useState, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { ChunkLesson } from "@/components/ChunkLesson";
import { BookOpen, ChevronRight, Loader2, Sparkles, Check } from "lucide-react";
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
  const [generatingForKp, setGeneratingForKp] = useState<string | null>(null);

  useEffect(() => {
    Promise.all([
      fetch(`/api/courses/${id}/outline`).then(r => r.ok ? r.json() : []),
      fetch(`/api/courses/${id}/lessons`).then(r => r.ok ? r.json() : []),
      fetch(`/api/courses/${id}/mastery`).then(r => r.ok ? r.json() : []),
    ]).then(([nodes, lessons, mastery]) => {
      const masteryMap = new Map(
        (mastery as { concept_id: string; current_level: MasteryLevelV2 }[])
          .map(m => [m.concept_id, m.current_level])
      );
      const lessonMap = new Map(
        (lessons as Lesson[]).map(l => [l.knowledge_point_id, l.id])
      );

      // Show all knowledge_point nodes, mark which have lessons
      const kps = (nodes as { id: string; title: string; type: string }[])
        .filter(n => n.type === "knowledge_point")
        .map(n => ({
          id: n.id,
          title: n.title,
          level: masteryMap.get(n.id) ?? "unseen" as MasteryLevelV2,
          hasLesson: lessonMap.has(n.id),
          lessonId: lessonMap.get(n.id) ?? null,
        }));

      setItems(kps);
      setLoading(false);
    });
  }, [id]);

  async function handleKpClick(kp: KnowledgePointItem) {
    if (kp.hasLesson && kp.lessonId) {
      // Already has lesson — open it
      openLesson(kp.lessonId);
      return;
    }

    // Generate lesson for this KP on-demand
    setGeneratingForKp(kp.id);
    try {
      const res = await fetch(`/api/courses/${id}/lessons/generate-one`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ knowledge_point_id: kp.id }),
      });

      if (res.ok) {
        const data = await res.json();
        // Update the item to reflect the new lesson
        setItems(prev => prev.map(item =>
          item.id === kp.id
            ? { ...item, hasLesson: true, lessonId: data.lesson_id }
            : item
        ));
        // Open the newly generated lesson
        openLesson(data.lesson_id);
      }
    } catch {
      // silent fail
    }
    setGeneratingForKp(null);
  }

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
            {isZh ? "选择一个知识点，AI 会生成互动课程" : "Pick a topic — AI generates an interactive lesson"}
          </p>
        </div>
      </div>

      {items.length === 0 ? (
        <div className="ui-empty">
          <BookOpen size={32} className="mx-auto mb-3" style={{ color: "var(--border)" }} />
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {isZh ? "还没有知识点。先创建课程大纲。" : "No knowledge points yet. Create a course outline first."}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item, i) => {
            const config = levelConfig[item.level];
            const isGenerating = generatingForKp === item.id;
            return (
              <button
                key={item.id}
                onClick={() => !isGenerating && handleKpClick(item)}
                disabled={isGenerating}
                className="w-full ui-panel p-4 flex items-center gap-4 text-left cursor-pointer group disabled:opacity-70"
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-xs font-bold"
                  style={{ backgroundColor: config.bgColor, color: config.color, border: `1px solid ${config.color}20` }}
                >
                  {item.hasLesson ? <Check size={16} /> : i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <p className="text-sm font-medium truncate">{item.title}</p>
                  <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                    {isGenerating
                      ? (isZh ? "正在生成互动课程..." : "Generating interactive lesson...")
                      : item.hasLesson
                        ? (isZh ? "点击复习" : "Click to review")
                        : (isZh ? "点击生成" : "Click to generate")}
                  </p>
                </div>
                {isGenerating ? (
                  <Loader2 size={16} className="animate-spin shrink-0" style={{ color: "var(--accent)" }} />
                ) : !item.hasLesson ? (
                  <Sparkles size={16} className="shrink-0 opacity-30 group-hover:opacity-100 transition-opacity" style={{ color: "var(--accent)" }} />
                ) : (
                  <ChevronRight size={16} className="shrink-0 opacity-30 group-hover:opacity-100 transition-opacity" style={{ color: "var(--text-secondary)" }} />
                )}
              </button>
            );
          })}
        </div>
      )}
    </div>
  );
}
