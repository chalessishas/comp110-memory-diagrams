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
      className="-[20px] p-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <Clock3 size={16} />
        <h3 className="text-sm font-medium">Study Time</h3>
      </div>

      <div className="flex items-end gap-1.5 h-20 mb-3">
        {weekly.map((day, i) => {
          const height = day.totalMs > 0 ? Math.max((day.totalMs / maxMs) * 100, 8) : 4;
          const isToday = i === weekly.length - 1;
          return (
            <div key={day.day} className="flex-1 flex flex-col items-center gap-1">
              <div
                className="w-full"
              />
              <span className="text-[10px]">
                {formatShortDate(day.day)}
              </span>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-3 gap-3 mt-4">
        <div>
          <p className="text-xs">Today</p>
          <p className="text-lg">{formatDuration(todayMs)}</p>
        </div>
        <div>
          <p className="text-xs">This Week</p>
          <p className="text-lg">{formatDuration(weekly.reduce((s, d) => s + d.totalMs, 0))}</p>
        </div>
        <div>
          <p className="text-xs">Daily Avg</p>
          <p className="text-lg">{formatDuration(allTime.avgPerDay)}</p>
        </div>
      </div>

      {allTime.totalMs > 60_000 && (
        <div className="mt-5 pt-4">
          <p className="text-xs mb-2">Time Distribution</p>
          <div className="ui-progress-track">
            {allTime.byMode.solving > 0 && (
              <div />
            )}
            {allTime.byMode.reviewing > 0 && (
              <div />
            )}
            {allTime.byMode.studying > 0 && (
              <div />
            )}
          </div>
          <div className="flex gap-3 mt-2">
            <span className="text-[10px] flex items-center gap-1">
              <span className="w-2 h-2" /> Solving
            </span>
            <span className="text-[10px] flex items-center gap-1">
              <span className="w-2 h-2" /> Reviewing
            </span>
            <span className="text-[10px] flex items-center gap-1">
              <span className="w-2 h-2" /> Studying
            </span>
          </div>
        </div>
      )}
    </div>
  );
}
