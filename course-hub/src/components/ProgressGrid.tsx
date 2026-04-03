"use client";

import { masteryColors, masteryLabels } from "@/lib/mastery";
import type { OutlineNode, MasteryLevel } from "@/types";

interface KPMastery {
  node: OutlineNode;
  level: MasteryLevel;
  rate: number;
  total: number;
}

export function ProgressGrid({ data }: { data: KPMastery[] }) {
  if (data.length === 0) {
    return (
      <p className="text-sm py-8 text-center" style={{ color: "var(--text-secondary)" }}>
        No knowledge points to track yet.
      </p>
    );
  }

  const grouped = {
    mastered: data.filter((d) => d.level === "mastered"),
    reviewing: data.filter((d) => d.level === "reviewing"),
    weak: data.filter((d) => d.level === "weak"),
    untested: data.filter((d) => d.level === "untested"),
  };

  return (
    <div>
      <div className="flex gap-4 mb-6">
        {(["mastered", "reviewing", "weak", "untested"] as MasteryLevel[]).map((level) => (
          <div key={level} className="flex items-center gap-1.5">
            <div className="w-3 h-3 rounded" style={{ backgroundColor: masteryColors[level] }} />
            <span className="text-xs" style={{ color: "var(--text-secondary)" }}>
              {masteryLabels[level]} ({grouped[level].length})
            </span>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-1.5">
        {data.map((item) => (
          <div key={item.node.id} className="relative group">
            <div
              className="w-10 h-10 rounded-lg transition-transform hover:scale-110"
              style={{ backgroundColor: masteryColors[item.level] }}
            />
            <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 rounded text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none z-10"
              style={{ backgroundColor: "var(--text-primary)", color: "var(--bg-surface)" }}
            >
              {item.node.title}
              {item.total > 0 && ` — ${Math.round(item.rate * 100)}% (${item.total} attempts)`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
