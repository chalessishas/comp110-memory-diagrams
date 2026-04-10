"use client";

import { useMemo } from "react";
import { loadCards } from "@/lib/spaced-repetition";
import { useI18n } from "@/lib/i18n";

function getDayLabel(date: Date, locale: string): string {
  return date.toLocaleDateString(locale === "zh" ? "zh-CN" : "en-US", { weekday: "short" });
}

export function ReviewSparkline({ questionIds }: { questionIds?: string[] }) {
  const { t, locale } = useI18n();

  const bars = useMemo(() => {
    const cards = loadCards();
    const filtered = questionIds
      ? cards.filter((c) => questionIds.includes(c.question_id))
      : cards;

    const today = new Date();
    today.setHours(0, 0, 0, 0);

    return Array.from({ length: 7 }, (_, i) => {
      const day = new Date(today);
      day.setDate(today.getDate() + i);
      const nextDay = new Date(day);
      nextDay.setDate(day.getDate() + 1);

      const count = filtered.filter((c) => {
        const due = new Date(c.card.due);
        return due >= day && due < nextDay;
      }).length;

      return { label: getDayLabel(day, locale), count, isToday: i === 0 };
    });
  }, [questionIds, locale]);

  const max = Math.max(...bars.map((b) => b.count), 1);
  const total = bars.reduce((s, b) => s + b.count, 0);

  if (total === 0) {
    return (
      <p className="text-xs mt-4" style={{ color: "var(--text-muted)" }}>
        {t("review.noUpcoming")}
      </p>
    );
  }

  return (
    <div className="mt-5 w-full max-w-sm mx-auto">
      <p className="text-[11px] font-medium tracking-wide mb-3 text-center" style={{ color: "var(--text-muted)" }}>
        {t("review.upcoming7Days")}
      </p>
      <div className="flex items-end justify-between gap-1.5 h-16">
        {bars.map((bar, i) => (
          <div key={i} className="flex flex-col items-center gap-1 flex-1">
            <div
              className="w-full rounded-t-md transition-all"
              style={{
                height: `${Math.max(4, Math.round((bar.count / max) * 52))}px`,
                backgroundColor: bar.isToday ? "var(--accent)" : "var(--border)",
                opacity: bar.count === 0 ? 0.3 : 1,
              }}
            />
            {bar.count > 0 && (
              <span className="text-[9px]" style={{ color: bar.isToday ? "var(--accent)" : "var(--text-muted)" }}>
                {bar.count}
              </span>
            )}
          </div>
        ))}
      </div>
      <div className="flex justify-between gap-1.5 mt-1">
        {bars.map((bar, i) => (
          <div key={i} className="flex-1 text-center">
            <span
              className="text-[9px] font-medium"
              style={{ color: bar.isToday ? "var(--accent)" : "var(--text-muted)" }}
            >
              {bar.label}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
