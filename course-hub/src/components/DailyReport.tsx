"use client";

import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { TrendingUp, BookOpen, Target, AlertTriangle, ArrowUpCircle, ChevronDown, ChevronUp } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { levelConfig } from "@/lib/mastery-v2";
import type { MasteryLevelV2 } from "@/types";
import type { DailyReportData } from "@/app/api/courses/[id]/daily-report/route";

type DayStats = DailyReportData["weekHistory"][number];

const DAY_LABELS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const DAY_LABELS_ZH = ["日", "一", "二", "三", "四", "五", "六"];

export function DailyReport({ courseId }: { courseId: string }) {
  const { locale } = useI18n();
  const isZh = locale === "zh";
  const [data, setData] = useState<DailyReportData | null>(null);
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState(false);

  useEffect(() => {
    fetch(`/api/courses/${courseId}/daily-report`)
      .then(r => r.ok ? r.json() : null)
      .then(d => { setData(d); setLoading(false); })
      .catch(() => setLoading(false));
  }, [courseId]);

  if (loading) {
    return (
      <div className="ui-panel p-5 animate-pulse">
        <div className="h-5 rounded" style={{ backgroundColor: "var(--border)", width: "40%" }} />
        <div className="h-20 rounded mt-3" style={{ backgroundColor: "var(--border)" }} />
      </div>
    );
  }

  if (!data) return null;

  const { today, weekHistory, mastery, troubleSpots } = data;
  const hasActivity = today.attempted > 0 || today.lessonsCompleted > 0 || today.lessonsStarted > 0;
  const weekTotal = weekHistory.reduce((s: number, d: DayStats) => s + d.attempted, 0);
  const weekMaxAttempts = Math.max(...weekHistory.map((d: DayStats) => d.attempted), 1);

  return (
    <div className="ui-panel overflow-hidden">
      {/* Header — always visible */}
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-5 flex items-center gap-3 cursor-pointer text-left"
        style={{ borderBottom: expanded ? "1px solid var(--border)" : "none" }}
      >
        <div
          className="w-9 h-9 flex items-center justify-center shrink-0"
          style={{
            backgroundColor: "rgba(99, 102, 241, 0.1)",
            color: "var(--accent)",
            borderRadius: "var(--radius-md)",
          }}
        >
          <TrendingUp size={16} />
        </div>
        <div className="flex-1 min-w-0">
          <p className="text-sm font-semibold">
            {isZh ? "今日学情" : "Today's Progress"}
          </p>
          <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
            {hasActivity
              ? isZh
                ? `${today.attempted} 道题 · ${today.accuracy}% 正确率${today.lessonsCompleted > 0 ? ` · ${today.lessonsCompleted} 课完成` : ""}`
                : `${today.attempted} questions · ${today.accuracy}% accuracy${today.lessonsCompleted > 0 ? ` · ${today.lessonsCompleted} lessons` : ""}`
              : isZh ? "今天还没开始学习" : "No activity yet today"
            }
          </p>
        </div>
        <div className="flex items-center gap-2">
          {today.levelUps.length > 0 && (
            <span
              className="flex items-center gap-1 text-xs font-semibold px-2 py-0.5"
              style={{
                backgroundColor: "rgba(5, 150, 105, 0.1)",
                color: "var(--success)",
                borderRadius: "var(--radius-sm)",
              }}
            >
              <ArrowUpCircle size={12} />
              {today.levelUps.length}
            </span>
          )}
          {expanded ? <ChevronUp size={16} style={{ color: "var(--text-secondary)" }} /> : <ChevronDown size={16} style={{ color: "var(--text-secondary)" }} />}
        </div>
      </button>

      {/* Expanded content */}
      {expanded && (
        <div className="p-5 space-y-5">
          {/* Stats row */}
          <div className="grid grid-cols-3 gap-3">
            <StatCard
              icon={<Target size={14} />}
              label={isZh ? "做题" : "Questions"}
              value={today.attempted}
              sub={today.attempted > 0 ? `${today.accuracy}%` : "—"}
              color="var(--accent)"
            />
            <StatCard
              icon={<BookOpen size={14} />}
              label={isZh ? "课程" : "Lessons"}
              value={today.lessonsCompleted}
              sub={today.lessonsStarted > today.lessonsCompleted ? `+${today.lessonsStarted - today.lessonsCompleted} ${isZh ? "进行中" : "in progress"}` : "—"}
              color="var(--success)"
            />
            <StatCard
              icon={<ArrowUpCircle size={14} />}
              label={isZh ? "升级" : "Level Ups"}
              value={today.levelUps.length}
              sub={today.resolvedMisconceptions > 0 ? `${today.resolvedMisconceptions} ${isZh ? "误区解决" : "fixed"}` : "—"}
              color="var(--warning)"
            />
          </div>

          {/* Level-up celebrations */}
          {today.levelUps.length > 0 && (
            <div>
              <p className="text-xs font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>
                {isZh ? "今日突破" : "Level Ups Today"}
              </p>
              <div className="space-y-1.5">
                {today.levelUps.map((lu: DailyReportData["today"]["levelUps"][number]) => (
                  <div
                    key={lu.conceptId}
                    className="flex items-center gap-2 text-xs px-3 py-2 rounded-lg"
                    style={{ backgroundColor: "var(--bg-muted)" }}
                  >
                    <span className="flex-1 truncate font-medium">{lu.conceptTitle}</span>
                    <LevelBadge level={lu.from as MasteryLevelV2} isZh={isZh} />
                    <span style={{ color: "var(--text-secondary)" }}>→</span>
                    <LevelBadge level={lu.to as MasteryLevelV2} isZh={isZh} />
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* 7-day activity chart */}
          <div>
            <div className="flex items-center justify-between mb-2">
              <p className="text-xs font-semibold" style={{ color: "var(--text-secondary)" }}>
                {isZh ? "近 7 天" : "Last 7 Days"}
              </p>
              <p className="text-xs" style={{ color: "var(--text-secondary)" }}>
                {weekTotal} {isZh ? "道题" : "questions"}
              </p>
            </div>
            <div className="flex items-end gap-1.5" style={{ height: 56 }}>
              {weekHistory.map((day: DayStats) => {
                const d = new Date(day.date + "T12:00:00");
                const dayLabel = isZh ? DAY_LABELS_ZH[d.getDay()] : DAY_LABELS[d.getDay()];
                const barH = day.attempted > 0 ? Math.max((day.attempted / weekMaxAttempts) * 44, 4) : 0;
                const accuracy = day.attempted > 0 ? day.correct / day.attempted : 0;

                return (
                  <div key={day.date} className="flex-1 flex flex-col items-center gap-1">
                    <div className="w-full flex items-end justify-center" style={{ height: 44 }}>
                      {day.attempted > 0 ? (
                        <div
                          className="w-full max-w-[20px] rounded-sm transition-all"
                          style={{
                            height: barH,
                            backgroundColor: accuracy >= 0.8 ? "var(--success)" : accuracy >= 0.5 ? "var(--warning)" : "var(--danger)",
                            opacity: 0.7,
                          }}
                        />
                      ) : (
                        <div
                          className="w-full max-w-[20px] rounded-sm"
                          style={{ height: 4, backgroundColor: "var(--border)" }}
                        />
                      )}
                    </div>
                    <span className="text-[9px]" style={{ color: "var(--text-secondary)" }}>
                      {dayLabel}
                    </span>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Mastery distribution */}
          <div>
            <p className="text-xs font-semibold mb-2" style={{ color: "var(--text-secondary)" }}>
              {isZh ? "掌握度分布" : "Mastery Distribution"}
            </p>
            <div className="h-2.5 rounded-full overflow-hidden flex" style={{ backgroundColor: "var(--border)" }}>
              {(["mastered", "proficient", "practiced", "exposed"] as MasteryLevelV2[]).map(level => {
                const pct = mastery.total > 0 ? (mastery[level] / mastery.total) * 100 : 0;
                if (pct === 0) return null;
                return (
                  <div
                    key={level}
                    style={{ width: `${pct}%`, backgroundColor: levelConfig[level].color }}
                    className="h-full transition-all"
                  />
                );
              })}
            </div>
            <div className="flex flex-wrap gap-x-4 gap-y-1 mt-2">
              {(["mastered", "proficient", "practiced", "exposed", "unseen"] as MasteryLevelV2[]).map(level => {
                const count = mastery[level];
                if (count === 0) return null;
                return (
                  <span key={level} className="flex items-center gap-1.5 text-[10px]" style={{ color: "var(--text-secondary)" }}>
                    <span className="w-2 h-2 rounded-full inline-block" style={{ backgroundColor: levelConfig[level].color }} />
                    {isZh ? levelConfig[level].labelZh : levelConfig[level].label} {count}
                  </span>
                );
              })}
            </div>
          </div>

          {/* Trouble spots */}
          {troubleSpots.length > 0 && (
            <div>
              <p className="text-xs font-semibold mb-2 flex items-center gap-1.5" style={{ color: "var(--danger)" }}>
                <AlertTriangle size={12} />
                {isZh ? "今日薄弱点" : "Trouble Spots"}
              </p>
              <div className="space-y-1.5">
                {troubleSpots.map((ts: DailyReportData["troubleSpots"][number]) => {
                  const rate = Math.round((ts.correct / ts.attempted) * 100);
                  return (
                    <div
                      key={ts.conceptId}
                      className="flex items-center gap-2 text-xs px-3 py-2 rounded-lg"
                      style={{ backgroundColor: "var(--bg-muted)" }}
                    >
                      <span className="flex-1 truncate">{ts.conceptTitle}</span>
                      <span className="font-mono tabular-nums" style={{ color: rate < 40 ? "var(--danger)" : "var(--warning)" }}>
                        {ts.correct}/{ts.attempted} ({rate}%)
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

function StatCard({ icon, label, value, sub, color }: {
  icon: ReactNode;
  label: string;
  value: number;
  sub: string;
  color: string;
}) {
  return (
    <div className="p-3 rounded-xl" style={{ backgroundColor: "var(--bg-muted)" }}>
      <div className="flex items-center gap-1.5 mb-1.5">
        <span style={{ color }}>{icon}</span>
        <span className="text-[10px] font-semibold uppercase tracking-wider" style={{ color: "var(--text-secondary)" }}>
          {label}
        </span>
      </div>
      <p className="text-xl font-bold tabular-nums">{value}</p>
      <p className="text-[10px] mt-0.5" style={{ color: "var(--text-secondary)" }}>
        {sub}
      </p>
    </div>
  );
}

function LevelBadge({ level, isZh }: { level: MasteryLevelV2; isZh: boolean }) {
  const config = levelConfig[level];
  if (!config) return <span className="text-[10px]">{level}</span>;
  return (
    <span
      className="text-[10px] font-semibold px-1.5 py-0.5 rounded"
      style={{ backgroundColor: config.bgColor, color: config.color }}
    >
      {isZh ? config.labelZh : config.label}
    </span>
  );
}
