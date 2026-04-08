"use client";

import { useEffect, useState } from "react";
import { Flame, Shield, Target } from "lucide-react";
import { getStreakData, getWeekHistory, type StreakData } from "@/lib/streaks";
import { useI18n } from "@/lib/i18n";

const DAY_NAMES = ["S", "M", "T", "W", "T", "F", "S"];

export function StreakBadge() {
  const { t } = useI18n();
  const [data, setData] = useState<StreakData | null>(null);
  const [open, setOpen] = useState(false);
  const [week, setWeek] = useState(getWeekHistory());

  useEffect(() => {
    setData(getStreakData());
    setWeek(getWeekHistory());
    const refresh = () => {
      setData(getStreakData());
      setWeek(getWeekHistory());
    };
    window.addEventListener("coursehub-streak-updated", refresh);
    return () => window.removeEventListener("coursehub-streak-updated", refresh);
  }, []);

  if (!data || (data.currentStreak === 0 && data.todayMinutes === 0 && data.todayQuestions === 0)) return null;

  const goalProgress = data.dailyGoal > 0 ? Math.min((data.todayMinutes / data.dailyGoal) * 100, 100) : 0;

  return (
    <div className="relative">
      <button
        onClick={() => setOpen(!open)}
        className="flex items-center gap-1.5 px-2.5 py-1.5 rounded-xl text-xs font-semibold cursor-pointer transition-colors"
        style={{
          backgroundColor: data.currentStreak > 0 ? "#fef3c7" : "transparent",
          color: data.currentStreak > 0 ? "#f59e0b" : "var(--text-secondary)",
          border: "1px solid",
          borderColor: data.currentStreak > 0 ? "#fcd34d" : "var(--border)",
        }}
      >
        <Flame size={14} />
        {data.currentStreak}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div
            className="absolute right-0 top-full mt-2 w-72 p-5 rounded-md z-50"
            style={{
              backgroundColor: "var(--bg-surface)",
              border: "1px solid var(--border)",
            }}
          >
            {/* Streak count */}
            <div className="text-center mb-4">
              <Flame size={28} className="mx-auto mb-2" style={{ color: "#f59e0b" }} />
              <p className="text-3xl font-bold">{data.currentStreak}</p>
              <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                {t("streak.dayStreak")}{data.longestStreak > data.currentStreak ? ` (${t("streak.best")} ${data.longestStreak})` : ""}
              </p>
            </div>

            {/* Daily goal progress */}
            <div className="mb-4 p-3 rounded-xl" style={{ backgroundColor: "var(--bg-muted)" }}>
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="flex items-center gap-1">
                  <Target size={12} /> {t("streak.dailyGoal")}
                </span>
                <span>{data.todayMinutes}/{data.dailyGoal} min</span>
              </div>
              <div className="h-2 rounded-full overflow-hidden" style={{ backgroundColor: "var(--border)" }}>
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${goalProgress}%`,
                    backgroundColor: goalProgress >= 100 ? "#16a34a" : "var(--accent)",
                  }}
                />
              </div>
            </div>

            {/* Week view */}
            <div className="flex justify-between">
              {week.map((day) => {
                const d = new Date(day.day + "T12:00:00");
                return (
                  <div key={day.day} className="flex flex-col items-center gap-1">
                    <div
                      className="w-7 h-7 rounded-full flex items-center justify-center text-[10px]"
                      style={{
                        backgroundColor: day.completed
                          ? "#f59e0b"
                          : day.minutes > 0
                          ? "#fef3c7"
                          : "var(--bg-muted)",
                        color: day.completed ? "white" : "var(--text-secondary)",
                        fontWeight: day.completed ? 600 : 400,
                      }}
                    >
                      {day.completed ? "✓" : ""}
                    </div>
                    <span className="text-[9px]" style={{ color: "var(--text-secondary)" }}>
                      {DAY_NAMES[d.getDay()]}
                    </span>
                  </div>
                );
              })}
            </div>

            {/* Freeze status */}
            <div
              className="mt-3 pt-3 flex items-center gap-2 text-[10px]"
              style={{ borderTop: "1px solid var(--border)", color: "var(--text-secondary)" }}
            >
              <Shield size={11} />
              {data.freezeAvailable ? t("streak.freezeAvailable") : t("streak.freezeUsed")}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
