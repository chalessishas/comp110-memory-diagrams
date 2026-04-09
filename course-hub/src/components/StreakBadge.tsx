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
        className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium cursor-pointer"
      >
        <Flame size={14} />
        {data.currentStreak}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div
            className="absolute right-0 top-full mt-2 w-72 p-5 -[20px] z-50"
          >
            <div className="text-center mb-4">
              <Flame size={28} className="mx-auto mb-2" />
              <p className="text-3xl">{data.currentStreak}</p>
              <p className="text-xs">
                {t("streak.dayStreak")}{data.longestStreak > data.currentStreak ? ` (${t("streak.best")} ${data.longestStreak})` : ""}
              </p>
            </div>

            <div className="mb-4 p-3 -[14px]">
              <div className="flex items-center justify-between text-xs mb-2">
                <span className="flex items-center gap-1">
                  <Target size={12} /> {t("streak.dailyGoal")}
                </span>
                <span>{data.todayMinutes}/{data.dailyGoal} min</span>
              </div>
              <div className="ui-progress-track">
                <div
                  className="ui-progress-bar"
                />
              </div>
            </div>

            <div className="flex justify-between">
              {week.map((day) => {
                const d = new Date(day.day + "T12:00:00");
                return (
                  <div key={day.day} className="flex flex-col items-center gap-1">
                    <div
                      className="w-7 h-7 flex items-center justify-center text-[10px]"
                    >
                      {day.completed ? "\u2713" : ""}
                    </div>
                    <span className="text-[9px]">
                      {DAY_NAMES[d.getDay()]}
                    </span>
                  </div>
                );
              })}
            </div>

            <div
              className="mt-3 pt-3 flex items-center gap-2 text-[10px]"
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
