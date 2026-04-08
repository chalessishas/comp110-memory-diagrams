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
      <div className="ui-empty">
        <p className="text-sm" style={{ color: "var(--text-secondary)" }}>
          No knowledge points to track yet.
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
        <div className="ui-kicker mb-3">Progress</div>
        <h3 className="text-2xl font-semibold">Knowledge Point Mastery</h3>
        <p className="ui-copy mt-2">
          A grayscale map of what feels solid, shaky, or still untouched.
        </p>
      </div>

      <div className="flex flex-wrap gap-3 mb-6">
        {(["mastered", "reviewing", "weak", "untested"] as MasteryLevel[]).map((level) => (
          <div
            key={level}
            className="flex items-center gap-2 rounded px-3 py-2"
            style={{ border: "1px solid var(--border)", backgroundColor: "var(--bg-surface)" }}
          >
            <div className="w-3.5 h-3.5 rounded" style={{ backgroundColor: masteryColors[level] }} />
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
              className="w-12 h-12 rounded-md"
              style={{ backgroundColor: masteryColors[item.level], border: "1px solid var(--border)" }}
            />
            <div
              className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 px-3 py-2 rounded-md text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none z-10"
              style={{ backgroundColor: "var(--text-primary)", color: "var(--bg-surface)" }}
            >
              {item.node.title}
              {item.total > 0 && ` • ${Math.round(item.rate * 100)}% (${item.total} attempts)`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
