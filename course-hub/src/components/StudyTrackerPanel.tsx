"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { Activity, BookOpenText, Brain, Clock3, PauseCircle } from "lucide-react";
import type { StudyMode } from "@/types";
import {
  STUDY_TRACKER_UPDATED_EVENT,
  formatDuration,
  getStudySummary,
  getWeeklySummary,
  recordStudyTime,
  type StudySummary,
} from "@/lib/study-tracker";
import { useI18n } from "@/lib/i18n";

const IDLE_THRESHOLD_MS = 20_000;

const MODE_ICONS: Record<StudyMode, typeof Brain> = {
  solving: Brain,
  reviewing: BookOpenText,
  studying: Clock3,
  idle: PauseCircle,
};

function modeTone(mode: StudyMode) {
  if (mode === "solving") return { backgroundColor: "var(--accent)", color: "var(--bg-surface)" };
  if (mode === "reviewing") return { backgroundColor: "var(--warning)", color: "var(--bg-surface)" };
  if (mode === "studying") return { backgroundColor: "var(--success)", color: "var(--bg-surface)" };
  return { backgroundColor: "var(--bg-muted)", color: "var(--text-primary)" };
}

function percent(total: number, value: number) {
  if (total <= 0) return 0;
  return Math.round((value / total) * 100);
}

function emptySummary(): StudySummary {
  return {
    totalMs: 0,
    byMode: {
      solving: 0,
      reviewing: 0,
      studying: 0,
      idle: 0,
    },
  };
}

function WeeklyMiniChart({ courseId }: { courseId?: string | null }) {
  const [weekly, setWeekly] = useState(() => getWeeklySummary(courseId));

  useEffect(() => {
    const refresh = () => setWeekly(getWeeklySummary(courseId));
    window.addEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
    return () => window.removeEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
  }, [courseId]);

  const maxMs = Math.max(...weekly.map((d) => d.totalMs), 1);
  const weekTotal = weekly.reduce((s, d) => s + d.totalMs, 0);

  return (
    <div>
      <div className="flex items-end gap-1.5 h-16">
        {weekly.map((day, i) => {
          const height = day.totalMs > 0 ? Math.max((day.totalMs / maxMs) * 100, 6) : 4;
          const isToday = i === weekly.length - 1;
          const d = new Date(day.day + "T12:00:00");
          const dayName = ["S", "M", "T", "W", "T", "F", "S"][d.getDay()];
          return (
            <div key={day.day} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full rounded-lg"
                style={{
                  height: `${height}%`,
                  backgroundColor: isToday ? "var(--accent)" : day.totalMs > 0 ? "var(--accent-muted)" : "var(--bg-muted)",
                  minHeight: "3px",
                }}
              />
              <span className="text-[9px]" style={{ color: isToday ? "var(--text-primary)" : "var(--text-muted)" }}>
                {dayName}
              </span>
            </div>
          );
        })}
      </div>
      <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
        Week total: {formatDuration(weekTotal)}
      </p>
    </div>
  );
}

export function StudyTrackerPanel({
  courseId,
  activeMode,
  title,
  description,
  track = true,
  className = "",
}: {
  courseId?: string | null;
  activeMode?: Exclude<StudyMode, "idle">;
  title?: string;
  description?: string;
  track?: boolean;
  className?: string;
}) {
  const { t } = useI18n();
  const [summary, setSummary] = useState<StudySummary>(emptySummary);
  const [liveMode, setLiveMode] = useState<StudyMode>(activeMode ?? "studying");
  const lastTickRef = useRef(0);
  const lastInteractionRef = useRef(0);
  const lastMouseMoveRef = useRef(0);

  const modeLabels: Record<StudyMode, string> = {
    solving: t("studyTracker.solving"),
    reviewing: t("studyTracker.reviewing"),
    studying: t("studyTracker.studying"),
    idle: t("studyTracker.idle"),
  };

  const breakdown = useMemo(
    () => [
      { key: "solving" as const, label: modeLabels.solving, value: summary.byMode.solving },
      { key: "reviewing" as const, label: modeLabels.reviewing, value: summary.byMode.reviewing },
      { key: "studying" as const, label: modeLabels.studying, value: summary.byMode.studying },
      { key: "idle" as const, label: modeLabels.idle, value: summary.byMode.idle },
    ],
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [summary, t]
  );

  useEffect(() => {
    setSummary(getStudySummary(courseId));
  }, [courseId]);

  useEffect(() => {
    const now = Date.now();
    lastTickRef.current = now;
    if (lastInteractionRef.current === 0) {
      lastInteractionRef.current = now;
    }
  }, []);

  useEffect(() => {
    const refresh = () => setSummary(getStudySummary(courseId));
    window.addEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
    return () => window.removeEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
  }, [courseId]);

  useEffect(() => {
    const markInteraction = () => {
      lastInteractionRef.current = Date.now();
    };

    const handleMouseMove = () => {
      const now = Date.now();
      if (now - lastMouseMoveRef.current < 3_000) return;
      lastMouseMoveRef.current = now;
      markInteraction();
    };

    window.addEventListener("pointerdown", markInteraction, { passive: true });
    window.addEventListener("keydown", markInteraction);
    window.addEventListener("scroll", markInteraction, { passive: true });
    window.addEventListener("touchstart", markInteraction, { passive: true });
    window.addEventListener("mousemove", handleMouseMove, { passive: true });

    return () => {
      window.removeEventListener("pointerdown", markInteraction);
      window.removeEventListener("keydown", markInteraction);
      window.removeEventListener("scroll", markInteraction);
      window.removeEventListener("touchstart", markInteraction);
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, []);

  useEffect(() => {
    if (!track || !activeMode) return;

    lastTickRef.current = Date.now();

    const interval = window.setInterval(() => {
      const now = Date.now();
      const delta = now - lastTickRef.current;
      lastTickRef.current = now;

      if (document.visibilityState !== "visible") return;

      const resolvedMode = now - lastInteractionRef.current > IDLE_THRESHOLD_MS ? "idle" : activeMode;
      setLiveMode(resolvedMode);
      recordStudyTime({ courseId, mode: resolvedMode, durationMs: delta });
      setSummary(getStudySummary(courseId));
    }, 1000);

    return () => {
      window.clearInterval(interval);
    };
  }, [activeMode, courseId, track]);

  useEffect(() => {
    if (!track || !activeMode) {
      setLiveMode(activeMode ?? "studying");
      return;
    }

    const resolvedMode = Date.now() - lastInteractionRef.current > IDLE_THRESHOLD_MS ? "idle" : activeMode;
    setLiveMode(resolvedMode);
  }, [activeMode, track]);

  const LiveIcon = MODE_ICONS[liveMode];

  return (
    <div className={`ui-panel p-5 md:p-6 ${className}`}>
      <div className="flex flex-col gap-4 md:flex-row md:items-start md:justify-between">
        <div>
          <div className="ui-kicker mb-3">{t("studyTracker.kicker")}</div>
          <h3 className="text-2xl" style={{ fontWeight: 600 }}>{title ?? t("studyTracker.title")}</h3>
          <p className="ui-copy mt-2 max-w-2xl">{description ?? t("studyTracker.desc")}</p>
        </div>
        {track && activeMode && (
          <div
            className="inline-flex items-center gap-2 rounded-xl px-4 py-2"
            style={modeTone(liveMode)}
          >
            <LiveIcon size={16} />
            <span className="text-sm font-medium">{modeLabels[liveMode]}</span>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 gap-4 mt-6 md:grid-cols-[220px_minmax(0,1fr)]">
        <div
          className="rounded-[20px] px-5 py-5"
          style={{ backgroundColor: "var(--bg-muted)" }}
        >
          <div className="flex items-center gap-2 text-sm font-medium" style={{ color: "var(--text-secondary)" }}>
            <Activity size={16} />
            {t("studyTracker.today")}
          </div>
          <p className="text-4xl tracking-tight mt-3" style={{ fontWeight: 600, color: "var(--text-primary)" }}>{formatDuration(summary.totalMs)}</p>
          <p className="text-xs mt-2" style={{ color: "var(--text-muted)" }}>
            {t("studyTracker.recordedDevice")}
          </p>
        </div>

        <div className="space-y-3">
          {breakdown.map((item) => (
            <div
              key={item.key}
              className="rounded-[16px] px-4 py-4"
              style={{ backgroundColor: "var(--bg-surface)", boxShadow: "var(--shadow-sm)" }}
            >
              <div className="flex items-center justify-between gap-3">
                <div>
                  <p className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{item.label}</p>
                  <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    {formatDuration(item.value)}
                  </p>
                </div>
                <span className="ui-badge">{percent(summary.totalMs, item.value)}%</span>
              </div>
              <div className="ui-progress-track mt-3">
                <div
                  className="ui-progress-bar"
                  style={{ width: `${percent(summary.totalMs, item.value)}%`, backgroundColor: modeTone(item.key).backgroundColor }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="mt-6 pt-5">
        <p className="text-xs font-medium mb-3" style={{ color: "var(--text-muted)" }}>{t("studyTracker.thisWeek")}</p>
        <WeeklyMiniChart courseId={courseId} />
      </div>
    </div>
  );
}
