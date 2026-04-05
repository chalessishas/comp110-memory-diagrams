"use client";

import { useEffect, useState } from "react";
import { Clock3 } from "lucide-react";
import {
  formatDuration,
  getWeeklySummary,
  getAllTimeStats,
  STUDY_TRACKER_UPDATED_EVENT,
} from "@/lib/study-tracker";

const DAY_NAMES = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];

function formatShortDate(dateStr: string) {
  const d = new Date(dateStr + "T12:00:00");
  return DAY_NAMES[d.getDay()];
}

export function StudyStatsCard() {
  const [weekly, setWeekly] = useState(getWeeklySummary());
  const [allTime, setAllTime] = useState(getAllTimeStats());

  useEffect(() => {
    const refresh = () => {
      setWeekly(getWeeklySummary());
      setAllTime(getAllTimeStats());
    };
    window.addEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
    const interval = setInterval(refresh, 30_000);
    return () => {
      window.removeEventListener(STUDY_TRACKER_UPDATED_EVENT, refresh);
      clearInterval(interval);
    };
  }, []);

  const maxMs = Math.max(...weekly.map((d) => d.totalMs), 1);
  const todayMs = weekly[weekly.length - 1]?.totalMs ?? 0;
  const hasData = allTime.totalMs > 0;

  if (!hasData) return null;

  return (
    <div
      className="rounded-[24px] p-6"
      style={{ backgroundColor: "var(--bg-surface)", border: "1px solid var(--border)" }}
    >
      <div className="flex items-center gap-2 mb-4">
        <Clock3 size={16} style={{ color: "var(--text-secondary)" }} />
        <h3 className="text-sm font-medium">Study Time</h3>
      </div>

      {/* Weekly bar chart */}
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
                  backgroundColor: isToday ? "var(--accent)" : day.totalMs > 0 ? "rgba(91, 108, 240, 0.35)" : "var(--border)",
                  minHeight: "3px",
                }}
              />
              <span className="text-[10px]" style={{ color: isToday ? "var(--text-primary)" : "var(--text-secondary)" }}>
                {formatShortDate(day.day)}
              </span>
            </div>
          );
        })}
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-3 gap-3 mt-4">
        <div>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>Today</p>
          <p className="text-lg font-semibold">{formatDuration(todayMs)}</p>
        </div>
        <div>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>This Week</p>
          <p className="text-lg font-semibold">{formatDuration(weekly.reduce((s, d) => s + d.totalMs, 0))}</p>
        </div>
        <div>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>Daily Avg</p>
          <p className="text-lg font-semibold">{formatDuration(allTime.avgPerDay)}</p>
        </div>
      </div>

      {/* Mode breakdown (all time, compact) */}
      {allTime.totalMs > 60_000 && (
        <div className="mt-4 pt-4" style={{ borderTop: "1px solid var(--border)" }}>
          <p className="text-xs mb-2" style={{ color: "var(--text-secondary)" }}>Time Distribution</p>
          <div className="flex h-2 rounded-full overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
            {allTime.byMode.solving > 0 && (
              <div style={{ width: `${(allTime.byMode.solving / allTime.totalMs) * 100}%`, backgroundColor: "var(--accent)" }} />
            )}
            {allTime.byMode.reviewing > 0 && (
              <div style={{ width: `${(allTime.byMode.reviewing / allTime.totalMs) * 100}%`, backgroundColor: "var(--warning)" }} />
            )}
            {allTime.byMode.studying > 0 && (
              <div style={{ width: `${(allTime.byMode.studying / allTime.totalMs) * 100}%`, backgroundColor: "var(--success)" }} />
            )}
          </div>
          <div className="flex gap-3 mt-2">
            <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--text-secondary)" }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--accent)" }} /> Solving
            </span>
            <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--text-secondary)" }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--warning)" }} /> Reviewing
            </span>
            <span className="text-[10px] flex items-center gap-1" style={{ color: "var(--text-secondary)" }}>
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: "var(--success)" }} /> Studying
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
