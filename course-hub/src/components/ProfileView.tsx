"use client";

import { AlertTriangle, Check, Brain, Activity } from "lucide-react";
import { useI18n } from "@/lib/i18n";
import { levelConfig } from "@/lib/mastery-v2";
import type { ElementMastery, Misconception, MasteryLevelV2 } from "@/types";

interface ProfileViewProps {
  courseTitle: string;
  totalKps: number;
  mastery: (ElementMastery & { conceptTitle: string })[];
  misconceptions: Misconception[];
  metacognitionData: { student_self_rating: number | null; ai_confidence_rating: string | null; meta_cognition_match: boolean | null }[];
  weeklyAttempts: number;
}

export function ProfileView({ courseTitle, totalKps, mastery, misconceptions, metacognitionData, weeklyAttempts }: ProfileViewProps) {
  const { locale } = useI18n();
  const isZh = locale === "zh";

  const counts: Record<MasteryLevelV2, number> = {
    unseen: totalKps,
    exposed: 0,
    practiced: 0,
    proficient: 0,
    mastered: 0,
  };

  for (const m of mastery) {
    const level = m.current_level as MasteryLevelV2;
    if (counts[level] !== undefined) {
      counts[level]++;
      counts.unseen--;
    }
  }

  const overallProgress = totalKps > 0 ? ((counts.proficient + counts.mastered) / totalKps) * 100 : 0;

  const active = misconceptions.filter(m => !m.resolved);
  const resolved = misconceptions.filter(m => m.resolved);

  const matchedChallenges = metacognitionData.filter(c => c.meta_cognition_match !== null);
  const metacognitionAccuracy = matchedChallenges.length > 0
    ? Math.round((matchedChallenges.filter(c => c.meta_cognition_match).length / matchedChallenges.length) * 100)
    : null;

  return (
    <div className="space-y-5">
      {/* Mastery Overview */}
      <div className="ui-panel p-6">
        <h2 className="text-lg font-semibold mb-5 tracking-wide">
          {isZh ? "掌握度概览" : "Mastery Overview"}
        </h2>

        {/* Progress bar */}
        <div className="mb-5">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm" style={{ color: "var(--text-secondary)" }}>
              {isZh ? `${Math.round(overallProgress)}% 已掌握` : `${Math.round(overallProgress)}% mastered`}
            </span>
          </div>
          <div className="h-[6px] rounded-full overflow-hidden flex" style={{ backgroundColor: "var(--bg-muted)" }}>
            {(["mastered", "proficient", "practiced", "exposed"] as MasteryLevelV2[]).map(level => {
              const pct = totalKps > 0 ? (counts[level] / totalKps) * 100 : 0;
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
        </div>

        {/* Level counts */}
        <div className="grid grid-cols-5 gap-2">
          {(["mastered", "proficient", "practiced", "exposed", "unseen"] as MasteryLevelV2[]).map(level => (
            <div key={level} className="text-center p-3 rounded-[12px]" style={{ backgroundColor: "var(--bg-muted)" }}>
              <p className="text-lg font-semibold" style={{ color: levelConfig[level].color }}>{counts[level]}</p>
              <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
                {isZh ? levelConfig[level].labelZh : levelConfig[level].label}
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Active Weaknesses */}
      {active.length > 0 && (
        <div className="ui-panel p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 tracking-wide">
            <AlertTriangle size={18} style={{ color: "var(--warning)" }} />
            {isZh ? "持续性弱点" : "Persistent Weaknesses"}
          </h2>
          <div className="space-y-3">
            {active.map(m => (
              <div key={m.id} className="p-4 rounded-[16px] flex gap-3" style={{ backgroundColor: "var(--bg-muted)" }}>
                <div
                  className="w-1 shrink-0 rounded-full"
                  style={{ backgroundColor: "var(--warning)" }}
                />
                <div>
                  <p className="text-sm font-medium">{m.misconception_description}</p>
                  <p className="text-xs mt-1" style={{ color: "var(--text-muted)" }}>
                    {isZh ? `出现 ${m.occurrence_count} 次` : `Occurred ${m.occurrence_count} times`}
                    {m.relapsed && (isZh ? " · 已复发" : " · Relapsed")}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Resolved */}
      {resolved.length > 0 && (
        <div className="ui-panel p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 tracking-wide">
            <Check size={18} style={{ color: "var(--success)" }} />
            {isZh ? "已克服" : "Overcome"}
          </h2>
          <div className="space-y-2">
            {resolved.map(m => (
              <div key={m.id} className="flex items-center gap-2 text-sm" style={{ color: "var(--text-secondary)" }}>
                <Check size={14} style={{ color: "var(--success)" }} />
                <span>{m.misconception_description}</span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Metacognition */}
      {metacognitionAccuracy !== null && (
        <div className="ui-panel p-6">
          <h2 className="text-lg font-semibold mb-3 flex items-center gap-2 tracking-wide">
            <Brain size={18} style={{ color: "var(--accent)" }} />
            {isZh ? "元认知准确度" : "Self-assessment Accuracy"}
          </h2>
          <p className="text-3xl font-semibold">{metacognitionAccuracy}%</p>
          <p className="text-xs mt-1" style={{ color: "var(--text-secondary)" }}>
            {isZh
              ? `你说"不确定"的题中，${metacognitionAccuracy}% 确实答错了。说明你对自己的判断相当准确。`
              : `Your self-assessment matched reality ${metacognitionAccuracy}% of the time.`}
          </p>
        </div>
      )}

      {/* Weekly summary */}
      <div className="ui-panel p-6">
        <h2 className="text-lg font-semibold mb-4 flex items-center gap-2 tracking-wide">
          <Activity size={18} style={{ color: "var(--accent)" }} />
          {isZh ? "本周学习" : "This Week"}
        </h2>
        <div className="grid grid-cols-2 gap-4">
          <div className="rounded-[16px] p-4" style={{ backgroundColor: "var(--bg-muted)" }}>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {isZh ? "答题次数" : "Questions Answered"}
            </p>
            <p className="text-2xl font-semibold mt-1">{weeklyAttempts}</p>
          </div>
          <div className="rounded-[16px] p-4" style={{ backgroundColor: "var(--bg-muted)" }}>
            <p className="text-xs" style={{ color: "var(--text-muted)" }}>
              {isZh ? "掌握的知识点" : "Concepts Proficient+"}
            </p>
            <p className="text-2xl font-semibold mt-1">{counts.proficient + counts.mastered}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
