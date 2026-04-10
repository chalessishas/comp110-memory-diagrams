"use client";

import { masteryColors } from "@/lib/mastery";
import type { OutlineNode, MasteryLevel } from "@/types";
import { useI18n } from "@/lib/i18n";

interface KPMastery {
  node: OutlineNode;
  level: MasteryLevel;
  rate: number;
  total: number;
}

export function ProgressGrid({ data }: { data: KPMastery[] }) {
  const { t } = useI18n();
  const masteryLabels: Record<MasteryLevel, string> = {
    mastered: t("progress.mastery.mastered"),
    reviewing: t("progress.mastery.reviewing"),
    weak: t("progress.mastery.weak"),
    untested: t("progress.mastery.untested"),
  };

  if (data.length === 0) {
    return (
      <div className="ui-empty">
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          {t("progress.grid.noKps")}
        </p>
      </div>
    );
  }

  const grouped = {
    mastered: data.filter((d) => d.level === "mastered"),
    reviewing: data.filter((d) => d.level === "reviewing"),
    weak: data.filter((d) => d.level === "weak"),
    untested: data.filter((d) => d.level === "untested"),
  };

  return (
    <div className="ui-panel p-5 md:p-6">
      <div className="mb-6">
        <div className="ui-kicker mb-3">{t("progress.grid.kicker")}</div>
        <h3 className="text-2xl" style={{ fontWeight: 600 }}>{t("progress.grid.title")}</h3>
        <p className="ui-copy mt-2">
          {t("progress.grid.desc")}
        </p>
      </div>

      <div className="flex flex-wrap gap-2.5 mb-6">
        {(["mastered", "reviewing", "weak", "untested"] as MasteryLevel[]).map((level) => (
          <div
            key={level}
            className="flex items-center gap-2 rounded-xl px-3 py-2"
            style={{ backgroundColor: "var(--bg-muted)" }}
          >
            <div className="w-3 h-3 rounded-full" style={{ backgroundColor: masteryColors[level] }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
              {masteryLabels[level]} ({grouped[level].length})
            </span>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2.5">
        {data.map((item) => (
          <div key={item.node.id} className="relative group">
            <div
              className="w-12 h-12 rounded-xl transition-transform hover:scale-105"
              style={{ backgroundColor: masteryColors[item.level] }}
            />
            <div
              className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 px-3 py-2 rounded-xl text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10"
              style={{ backgroundColor: "var(--bg-surface)", color: "var(--text-primary)", boxShadow: "var(--shadow-md)" }}
            >
              {item.node.title}
              {item.total > 0 && ` · ${Math.round(item.rate * 100)}% (${item.total} ${t("progress.grid.attempts")})`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
