"use client";

import { useEffect, useState } from "react";
import { Activity } from "lucide-react";
import { getTodayUsage, getWeeklyUsage, estimateCost, formatTokens } from "@/lib/usage-tracker";
import type { UsageRecord } from "@/lib/usage-tracker";
import { useI18n } from "@/lib/i18n";

export function UsagePanel() {
  const { t } = useI18n();
  const [today, setToday] = useState<UsageRecord | null>(null);
  const [weekly, setWeekly] = useState<UsageRecord[]>([]);

  useEffect(() => {
    setToday(getTodayUsage());
    setWeekly(getWeeklyUsage());
    const interval = setInterval(() => {
      setToday(getTodayUsage());
      setWeekly(getWeeklyUsage());
    }, 30_000);
    return () => clearInterval(interval);
  }, []);

  if (!today) return null;

  const hasAnyUsage = today.requests > 0 || weekly.some((d) => d.requests > 0);
  if (!hasAnyUsage) return null;

  const weeklyTotal = weekly.reduce(
    (s, d) => ({
      inputTokens: s.inputTokens + d.inputTokens,
      outputTokens: s.outputTokens + d.outputTokens,
      requests: s.requests + d.requests,
    }),
    { inputTokens: 0, outputTokens: 0, requests: 0 }
  );

  const weeklyCost = estimateCost(weeklyTotal.inputTokens, weeklyTotal.outputTokens);

  return (
    <div className="ui-panel p-5">
      <div className="flex items-center gap-2 mb-4">
        <Activity size={16} style={{ color: "var(--text-muted)" }} />
        <h3 className="text-sm font-medium">{t("usage.title")}</h3>
      </div>

      <div className="grid grid-cols-3 gap-3 mb-5">
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("usage.today")}</p>
          <p className="text-base font-semibold mt-0.5">{today.requests} {t("usage.calls")}</p>
          <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
            {formatTokens(today.inputTokens + today.outputTokens)} tokens
          </p>
        </div>
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("usage.thisWeek")}</p>
          <p className="text-base font-semibold mt-0.5">{weeklyTotal.requests} {t("usage.calls")}</p>
          <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>
            {formatTokens(weeklyTotal.inputTokens + weeklyTotal.outputTokens)} tokens
          </p>
        </div>
        <div>
          <p className="text-xs" style={{ color: "var(--text-muted)" }}>{t("usage.estCost")}</p>
          <p className="text-base font-semibold mt-0.5">${weeklyCost.toFixed(3)}</p>
          <p className="text-[10px]" style={{ color: "var(--text-muted)" }}>{t("usage.thisWeek")}</p>
        </div>
      </div>

      {/* Weekly bar chart */}
      <div className="flex items-end gap-1 h-12">
        {(() => {
          const maxReqs = Math.max(...weekly.map((d) => d.requests), 1);
          return weekly.map((day, i) => {
          const height = day.requests > 0 ? Math.max((day.requests / maxReqs) * 100, 8) : 4;
          const isToday = i === weekly.length - 1;
          return (
            <div key={day.date} className="flex-1">
              <div
                className="w-full rounded-full"
                style={{
                  height: `${height}%`,
                  backgroundColor: isToday
                    ? "var(--accent)"
                    : day.requests > 0
                    ? "var(--accent-light)"
                    : "var(--bg-muted)",
                  minHeight: "2px",
                }}
              />
            </div>
          );
        });
        })()}
      </div>
    </div>
  );
}
