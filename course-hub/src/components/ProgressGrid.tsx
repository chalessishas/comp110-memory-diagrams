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
        <p className="text-sm">
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
        <h3 className="text-2xl">Knowledge Point Mastery</h3>
        <p className="ui-copy mt-2">
          A grayscale map of what feels solid, shaky, or still untouched.
        </p>
      </div>

      <div className="flex flex-wrap gap-2.5 mb-6">
        {(["mastered", "reviewing", "weak", "untested"] as MasteryLevel[]).map((level) => (
          <div
            key={level}
            className="flex items-center gap-2 px-3 py-2"
          >
            <div className="w-3 h-3" />
            <span className="text-xs">
              {masteryLabels[level]} ({grouped[level].length})
            </span>
          </div>
        ))}
      </div>

      <div className="flex flex-wrap gap-2.5">
        {data.map((item) => (
          <div key={item.node.id} className="relative group">
            <div
              className="w-12 h-12"
            />
            <div
              className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 px-3 py-2 text-xs whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none z-10"
            >
              {item.node.title}
              {item.total > 0 && ` · ${Math.round(item.rate * 100)}% (${item.total} attempts)`}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
