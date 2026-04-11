"use client";

import { useEffect, useState } from "react";
import { Clock3 } from "lucide-react";
import {
  formatDuration,
  getWeeklySummary,
  getAllTimeStats,
  STUDY_TRACKER_UPDATED_EVENT,
} from "@/lib/study-tracker";
import { useI18n } from "@/lib/i18n";

const DAY_KEYS = ["misc.daySun", "misc.dayMon", "misc.dayTue", "misc.dayWed", "misc.dayThu", "misc.dayFri", "misc.daySat"] as const;

export function StudyStatsCard() {
  const { t } = useI18n();

  function formatShortDate(dateStr: string) {
    const d = new Date(dateStr + "T12:00:00");
    return t(DAY_KEYS[d.getDay()]);
  }
  const [weekly, setWeekly] = useState(getWeeklySummary());
  const [allTime, setAllTime] = useState(getAllTimeStats());

  useEffect(() => {
    const refresh = () => {
      setWeekly(getWeeklySummary());
      setAllTime(getAllTimeStats());
    };
    window.addEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
    return () => {
      window.removeEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
    };
  }, []);

  const maxMs = Math.max(...weekly.map((d) => d.totalMs), 1);
  const todayMs = weekly[weekly.length - 1]?.totalMs ?? 0;
  const hasData = allTime.totalMs > 0;

  if (!hasData) return null;

  return (
    <div
      className="rounded-[20px] p-6"
      style={{ backgroundColor: "var(--bg-surface)", boxShadow: "var(--shadow-card)" }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Clock3 size={16} style={{ color: "var(--text-muted)" }} />
        <h3 className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>{t("studyStats.title")}</h3>
      </div>

      <div className="flex items-end gap-1.5 h-20 mb-3">
        {weekly.map((day, i) => {
          const height = day.totalMs > 0 ? Math.max((day.totalMs / maxMs) * 100, 8) : 4;
          const isToday = i === weekly.length - 1;
          return (
            <div key={day.day} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full rounded-lg transition-all"
                style={{
                  height: `${height}%`,
                  backgroundColor: isToday ? "var(--accent)" : day.totalMs > 0 ? "var(--accent-muted)" : "var(--bg-muted)",
                  minHeight: "3px",
                }}
              />
              <span className="text-[10px]" style={{ color: isToday ? "var(--text-primary)" : "var(--text-muted)" }}>
                {formatShortDate(day.day)}
              </span>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-3 gap-3 mt-4">
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("studyStats.today")}</p>
          <p className="text-lg" style={{ fontWeight: 600 }}>{formatDuration(todayMs)}</p>
        </div>
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("studyStats.thisWeek")}</p>
          <p className="text-lg" style={{ fontWeight: 600 }}>{formatDuration(weekly.reduce((s, d) => s + d.totalMs, 0))}</p>
        </div>
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("studyStats.dailyAvg")}</p>
          <p className="text-lg" style={{ fontWeight: 600 }}>{formatDuration(allTime.avgPerDay)}</p>
        </div>
      </div>

      {allTime.totalMs > 60_000 && (
        <div className="mt-5 pt-4">
          <p className="text-xs mb-2" style={{ color: "var(--text-muted)" }}>{t("studyStats.distribution")}</p>
          <div className="ui-progress-track">
            {allTime.byMode.solving > 0 && (
              <div style={{ width: `${(allTime.byMode.solving / allTime.totalMs) * 100}%`, height: "100%", backgroundColor: "var(--accent)", display: "inline-block" }} />
            )}
            {allTime.byMode.reviewing > 0 && (
              <div style={{ width: `${(allTime.byMode.reviewing / allTime.totalMs) * 100}%`, height: "100%", backgroundColor: "var(--warning)", display: "inline-block" }} />
            )}
            {allTime.byMode.studying > 0 && (
              <div style={{ width: `${(allTime.byMode.studying / allTime.totalMs) * 100}%`, height: "100%", backgroundColor: "var(--success)", display: "inline-block" }} />
            )}
          </div>
          <div className="flex gap-3 mt-2">
            <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--accent)" }} /> {t("studyTracker.solving")}
            </span>
            <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--warning)" }} /> {t("studyTracker.reviewing")}
            </span>
            <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--text-muted)" }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--success)" }} /> {t("studyTracker.studying")}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
