"use client";

import { useEffect, useState } from "react";
import { X, Flame, Check, Calendar, TrendingUp } from "lucide-react";
import { getStreakData, getWeekHistory } from "@/lib/streaks";
import { getDueCards, loadCards } from "@/lib/spaced-repetition";
import { useI18n } from "@/lib/i18n";

interface MasteryLevelUp {
  element_name: string;
  current_level: string;
  level_reached_at: string;
}

interface Props {
  open: boolean;
  onClose: () => void;
  courseId: string;
  sessionAnswered: number;
  sessionCorrect: number;
  sessionMinutes: number;
  sessionStart: number; // Date.now() when session started, for mastery-summary API
}

const LEVEL_LABELS: Record<string, { en: string; zh: string; color: string }> = {
  exposed:   { en: "exposed",   zh: "初识",   color: "var(--text-secondary)" },
  practiced: { en: "practiced", zh: "练习中", color: "var(--warning)" },
  proficient:{ en: "proficient",zh: "熟练",   color: "var(--accent)" },
  mastered:  { en: "mastered",  zh: "已掌握", color: "var(--success)" },
};

export function SessionSummaryModal({ open, onClose, courseId, sessionAnswered, sessionCorrect, sessionMinutes, sessionStart }: Props) {
  const { locale } = useI18n();
  const isZh = locale === "zh";
  const [tomorrowDue, setTomorrowDue] = useState<number>(0);
  const [levelUps, setLevelUps] = useState<MasteryLevelUp[]>([]);

  useEffect(() => {
    if (!open) return;

    // Count cards due within next 24 hours
    const cards = loadCards();
    const tomorrow = new Date(Date.now() + 86_400_000);
    const due = getDueCards(cards).filter((c) => new Date(c.card.due) <= tomorrow);
    setTomorrowDue(due.length);

    // Fetch mastery level-ups since session start
    const since = new Date(sessionStart).toISOString();
    fetch(`/api/courses/${courseId}/mastery-summary?since=${encodeURIComponent(since)}`)
      .then((r) => r.ok ? r.json() : [])
      .then((data: MasteryLevelUp[]) => setLevelUps(data))
      .catch(() => {});
  }, [open, courseId, sessionStart]);

  if (!open) return null;

  const streak = getStreakData();
  const weekHistory = getWeekHistory();
  const accuracy = sessionAnswered > 0 ? Math.round((sessionCorrect / sessionAnswered) * 100) : 0;
  const goalMet = streak.todayQuestions >= Math.max(5, streak.dailyGoal) || streak.todayMinutes >= streak.dailyGoal;

  const DAY_LABELS_ZH = ["一", "二", "三", "四", "五", "六", "日"];
  const DAY_LABELS_EN = ["M", "T", "W", "T", "F", "S", "S"];

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
      style={{ backgroundColor: "rgba(0,0,0,0.5)" }}
      onClick={onClose}
    >
      <div
        className="w-full max-w-sm rounded-[24px] p-6 relative overflow-y-auto"
        style={{ backgroundColor: "var(--bg-card)", maxHeight: "90vh" }}
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 cursor-pointer"
          style={{ color: "var(--text-muted)" }}
        >
          <X size={18} />
        </button>

        {/* Header */}
        <div className="text-center mb-5">
          <div className="w-12 h-12 rounded-full flex items-center justify-center mx-auto mb-3"
            style={{ backgroundColor: "var(--success)", opacity: 0.9 }}>
            <Check size={24} color="white" />
          </div>
          <h2 className="text-lg font-semibold">
            {isZh ? "复习完成" : "Session Complete"}
          </h2>
        </div>

        {/* Session stats */}
        <div className="grid grid-cols-3 gap-3 mb-5">
          {[
            { value: sessionAnswered, label: isZh ? "题" : "questions" },
            { value: `${accuracy}%`, label: isZh ? "正确率" : "accuracy" },
            { value: sessionMinutes > 0 ? `${sessionMinutes}m` : "—", label: isZh ? "时长" : "time" },
          ].map((stat) => (
            <div key={stat.label} className="text-center p-3 rounded-xl" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-xl font-bold">{stat.value}</p>
              <p className="text-xs mt-0.5" style={{ color: "var(--text-secondary)" }}>{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Streak */}
        <div className="mb-5 p-4 rounded-xl" style={{ backgroundColor: "var(--bg-muted)" }}>
          <div className="flex items-center gap-2 mb-3">
            <Flame size={16} style={{ color: "var(--warning)" }} />
            <span className="text-sm font-medium">
              {isZh ? `连续学习 ${streak.currentStreak} 天` : `${streak.currentStreak}-day streak`}
            </span>
            {goalMet && (
              <span className="ml-auto text-xs px-2 py-0.5 rounded-full font-medium"
                style={{ backgroundColor: "var(--success)", color: "white" }}>
                {isZh ? "今日目标达成" : "Goal met!"}
              </span>
            )}
          </div>
          <div className="flex gap-1.5 justify-between">
            {weekHistory.map((day, i) => (
              <div key={i} className="flex flex-col items-center gap-1">
                <div
                  className="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-medium"
                  style={{
                    backgroundColor: day.completed ? "var(--success)" : "var(--bg-card)",
                    color: day.completed ? "white" : "var(--text-muted)",
                  }}
                >
                  {day.completed ? "✓" : (isZh ? DAY_LABELS_ZH[i] : DAY_LABELS_EN[i])}
                </div>
                <span className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                  {isZh ? DAY_LABELS_ZH[i] : DAY_LABELS_EN[i]}
                </span>
              </div>
            ))}
          </div>
        </div>

        {/* Mastery level-ups */}
        {levelUps.length > 0 && (
          <div className="mb-5 p-4 rounded-xl" style={{ backgroundColor: "var(--bg-muted)" }}>
            <div className="flex items-center gap-2 mb-3">
              <TrendingUp size={16} style={{ color: "var(--accent)" }} />
              <span className="text-sm font-medium">
                {isZh ? `${levelUps.length} 个知识点提升` : `${levelUps.length} knowledge point${levelUps.length > 1 ? "s" : ""} leveled up`}
              </span>
            </div>
            <div className="space-y-1.5">
              {levelUps.map((kp, i) => {
                const levelInfo = LEVEL_LABELS[kp.current_level] ?? { en: kp.current_level, zh: kp.current_level, color: "var(--text-secondary)" };
                return (
                  <div key={i} className="flex items-center justify-between">
                    <span className="text-sm truncate mr-2" style={{ maxWidth: "70%" }}>{kp.element_name}</span>
                    <span className="text-xs font-medium shrink-0" style={{ color: levelInfo.color }}>
                      → {isZh ? levelInfo.zh : levelInfo.en}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>
        )}

        {/* Tomorrow preview */}
        <div className="flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
          <Calendar size={14} />
          <span>
            {isZh
              ? `明天约有 ${tomorrowDue} 张卡片待复习`
              : `${tomorrowDue} card${tomorrowDue !== 1 ? "s" : ""} due tomorrow`}
          </span>
        </div>
      </div>
    </div>
  );
}
