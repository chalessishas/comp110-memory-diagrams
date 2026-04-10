"use client";

import { useEffect, useState, useCallback, use } from "react";
import { CourseTabs } from "@/components/CourseTabs";
import { ChunkLesson } from "@/components/ChunkLesson";
import { BookOpen, ChevronRight, Loader2, Sparkles, Check, Target } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { levelConfig } from "@/lib/mastery-v2";
import { getExamScope } from "@/lib/spaced-repetition";
import type { Lesson, LessonChunk, MasteryLevelV2 } from "@/types";

interface KnowledgePointItem {
  id: string;
  title: string;
  level: MasteryLevelV2;
  hasLesson: boolean;
  lessonId: string | null;
}

// Parse SSE text stream into individual events
function parseSSE(text: string): { event: string; data: string }[] {
  const events: { event: string; data: string }[] = [];
  const blocks = text.split("\n\n").filter(Boolean);
  for (const block of blocks) {
    let event = "message";
    let data = "";
    for (const line of block.split("\n")) {
      if (line.startsWith("event: ")) event = line.slice(7).trim();
      else if (line.startsWith("data: ")) data = line.slice(6);
    }
    if (data) events.push({ event, data });
  }
  return events;
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
  const [generateError, setGenerateError] = useState<string | null>(null);
  const [refreshKey, setRefreshKey] = useState(0);
  // Streaming state
  const [isStreaming, setIsStreaming] = useState(false);
  const [totalChunks, setTotalChunks] = useState(0);
  const [streamedCount, setStreamedCount] = useState(0);
  const [scopeKpIds, setScopeKpIds] = useState<Set<string> | null>(null);

  useEffect(() => {
    const scope = getExamScope(id);
    if (scope && scope.length > 0) setScopeKpIds(new Set(scope));
  }, [id]);

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
  }, [id, refreshKey]);

  // Fetch full chunks from server (needed for answers after streaming)
  const fetchFullChunks = useCallback(async (lessonId: string) => {
    try {
      const res = await fetch(`/api/courses/${id}/lessons/${lessonId}/chunks`);
      const data = res.ok ? await res.json() : [];
      setChunks(Array.isArray(data) ? data : []);
    } catch {
      // Keep whatever chunks we have from streaming
    }
  }, [id]);

  async function handleKpClick(kp: KnowledgePointItem) {
    if (kp.hasLesson && kp.lessonId) {
      openLesson(kp.lessonId);
      return;
    }

    // Generate lesson with streaming
    setGeneratingForKp(kp.id);
    setGenerateError(null);
    setIsStreaming(true);
    setStreamedCount(0);
    setTotalChunks(4); // default, updated when outline arrives
    setChunks([]);

    try {
      const res = await fetch(`/api/courses/${id}/lessons/generate-one`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ knowledge_point_id: kp.id, stream: true }),
      });

      if (!res.ok || !res.body) {
        setGenerateError(t("learn.generationFailed"));
        setIsStreaming(false);
        setGeneratingForKp(null);
        return;
      }

      // Read SSE stream progressively
      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";
      let lessonId: string | null = null;

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Process complete SSE events (delimited by \n\n)
        const events = parseSSE(buffer);
        // Keep only the last incomplete block in buffer
        const lastDoubleNewline = buffer.lastIndexOf("\n\n");
        buffer = lastDoubleNewline >= 0 ? buffer.slice(lastDoubleNewline + 2) : buffer;

        for (const { event, data } of events) {
          try {
            const parsed = JSON.parse(data);

            if (event === "outline") {
              setTotalChunks(parsed.total_chunks ?? 4);
            }

            if (event === "lesson") {
              lessonId = parsed.lesson_id;
              setActiveLessonId(lessonId);
              setItems(prev => prev.map(item =>
                item.id === kp.id
                  ? { ...item, hasLesson: true, lessonId: parsed.lesson_id }
                  : item
              ));
            }

            if (event === "chunk") {
              setStreamedCount(c => c + 1);
              // Add placeholder chunk for streaming preview
              // (will be replaced by full fetch with answers)
              setChunks(prev => {
                const exists = prev.some(c => c.chunk_index === parsed.chunk_index);
                if (exists) return prev;
                const placeholder: LessonChunk = {
                  id: `stream-${parsed.chunk_index}`,
                  lesson_id: lessonId ?? "",
                  chunk_index: parsed.chunk_index,
                  content: parsed.content,
                  checkpoint_type: parsed.checkpoint_type,
                  checkpoint_prompt: parsed.checkpoint_prompt,
                  checkpoint_answer: null, // not sent in stream for security
                  checkpoint_options: parsed.checkpoint_options,
                  key_terms: parsed.key_terms ?? null,
                  widget_code: null, widget_description: null, widget_challenge: null,
                  checkpoint_core_elements: null,
                  remediation_content: null, remediation_question: null, remediation_answer: null,
                };
                return [...prev, placeholder].sort((a, b) => a.chunk_index - b.chunk_index);
              });
            }

            if (event === "done") {
              if (parsed.cached && parsed.lesson_id) {
                // Lesson already existed — just open it
                lessonId = parsed.lesson_id;
                setActiveLessonId(lessonId);
                setItems(prev => prev.map(item =>
                  item.id === kp.id
                    ? { ...item, hasLesson: true, lessonId: parsed.lesson_id }
                    : item
                ));
              }
              // Fetch full chunks with answers from DB
              if (lessonId) await fetchFullChunks(lessonId);
            }

            if (event === "error") {
              setGenerateError(parsed.message ?? t("learn.generationFailedShort"));
            }
          } catch {
            // Skip unparseable events
          }
        }
      }
    } catch {
      setGenerateError(t("learn.networkError"));
    }

    setIsStreaming(false);
    setGeneratingForKp(null);
  }

  async function openLesson(lessonId: string) {
    setActiveLessonId(lessonId);
    setLoadingChunks(true);
    try {
      const res = await fetch(`/api/courses/${id}/lessons/${lessonId}/chunks`);
      const data = res.ok ? await res.json() : [];
      setChunks(Array.isArray(data) ? data : []);
    } catch {
      setChunks([]);
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
    // Show streaming progress while generating
    if (isStreaming && chunks.length === 0) {
      return (
        <div>
          <CourseTabs courseId={id} />
          <div className="text-center py-16">
            <Loader2 size={24} className="animate-spin mx-auto mb-4" style={{ color: "var(--accent)" }} />
            <p className="text-sm font-medium mb-1">
              {t("learn.generatingLesson")}
            </p>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {isZh
                ? `已完成 ${streamedCount}/${totalChunks} 个教学环节`
                : `${streamedCount}/${totalChunks} sections ready`}
            </p>
          </div>
        </div>
      );
    }

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
          onClick={() => { setActiveLessonId(null); setChunks([]); setRefreshKey(k => k + 1); }}
          className="ui-button-ghost mb-4 !px-0"
        >
          ← {t("learn.backToTopics")}
        </button>
        <ChunkLesson
          chunks={chunks}
          courseId={id}
          lessonId={activeLessonId}
          totalChunks={isStreaming ? totalChunks : undefined}
          isStreaming={isStreaming}
        />
      </div>
    );
  }

  return (
    <div>
      <CourseTabs courseId={id} />

      <div className="flex items-center justify-between mb-8">
        <div>
          <h2 className="text-xl font-semibold tracking-wide">{t("tabs.learn")}</h2>
          <p className="text-sm mt-2" style={{ color: "var(--text-secondary)" }}>
            {t("learn.pickTopic")}
          </p>
        </div>
      </div>

      {generateError && (
        <div className="mb-4 px-4 py-3 rounded-xl text-sm" style={{ backgroundColor: "var(--bg-muted)", color: "var(--danger)" }}>
          {generateError}
        </div>
      )}

      {items.length === 0 ? (
        <div className="ui-empty">
          <BookOpen size={32} className="mx-auto mb-3" style={{ color: "var(--border)" }} />
          <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
            {t("learn.noKps")}
          </p>
        </div>
      ) : (
        <div className="space-y-2">
          {items.map((item, i) => {
            const config = levelConfig[item.level];
            const isGenerating = generatingForKp === item.id;
            const inScope = scopeKpIds?.has(item.id);
            return (
              <button
                key={item.id}
                onClick={() => !isGenerating && handleKpClick(item)}
                disabled={isGenerating}
                className="w-full ui-panel p-4 flex items-center gap-4 text-left cursor-pointer group disabled:opacity-70"
                style={scopeKpIds && !inScope ? { opacity: 0.45 } : undefined}
              >
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center shrink-0 text-xs font-semibold"
                  style={{ backgroundColor: config.bgColor, color: config.color, border: `1px solid ${config.color}20` }}
                >
                  {item.hasLesson ? <Check size={16} /> : i + 1}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <p className="text-sm font-medium truncate">{item.title}</p>
                    {inScope && (
                      <span className="shrink-0 flex items-center gap-0.5 text-[10px] px-1.5 py-0.5 rounded-full" style={{ backgroundColor: "var(--accent-light)", color: "var(--accent)" }}>
                        <Target size={8} />
                        {t("learn.examTag")}
                      </span>
                    )}
                  </div>
                  <p className="text-xs mt-0.5" style={{ color: "var(--text-muted)" }}>
                    {isGenerating
                      ? (isZh
                        ? `正在生成...（${streamedCount}/${totalChunks}）`
                        : `Generating... (${streamedCount}/${totalChunks})`)
                      : item.hasLesson
                        ? t("learn.clickToReview")
                        : t("learn.clickToGenerate")}
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
