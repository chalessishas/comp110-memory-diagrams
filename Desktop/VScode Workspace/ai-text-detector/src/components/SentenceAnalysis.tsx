"use client";

import { useState } from "react";
import type { SentenceScoreData } from "@/lib/analysis";

interface Props {
  sentenceScores: SentenceScoreData[];
}

function getHighlightColor(score: number): string {
  if (score > 70) return "bg-red-100/80";
  if (score > 30) return "bg-amber-100/60";
  return "bg-emerald-100/40";
}

function getLabelStyle(score: number): string {
  if (score > 70) return "text-red-700 bg-red-50 border-red-200";
  if (score > 30) return "text-amber-700 bg-amber-50 border-amber-200";
  return "text-emerald-700 bg-emerald-50 border-emerald-200";
}

export default function SentenceAnalysis({ sentenceScores }: Props) {
  const [selected, setSelected] = useState<number | null>(null);

  const aiCount = sentenceScores.filter((s) => s.aiScore > 70).length;
  const mixedCount = sentenceScores.filter(
    (s) => s.aiScore > 30 && s.aiScore <= 70
  ).length;
  const humanCount = sentenceScores.filter((s) => s.aiScore <= 30).length;

  return (
    <div className="space-y-4">
      <div className="bg-white rounded-2xl p-6 border border-[var(--card-border)] shadow-sm">
        <h3 className="text-sm font-semibold text-[var(--foreground)] mb-1">
          Sentence-Level Analysis
        </h3>
        <p className="text-xs text-[var(--muted)] mb-4">
          Each sentence scored independently by perplexity. Hover to highlight.
        </p>

        <div className="flex gap-4 text-xs mb-4">
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-red-200" />
            AI-like: {aiCount}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-amber-200" />
            Mixed: {mixedCount}
          </span>
          <span className="flex items-center gap-1.5">
            <span className="w-3 h-3 rounded bg-emerald-200" />
            Human-like: {humanCount}
          </span>
        </div>

        <div className="text-sm leading-[1.8]">
          {sentenceScores.map((s, i) => (
            <span
              key={i}
              className={`${getHighlightColor(s.aiScore)} ${selected === i ? "ring-2 ring-[var(--accent)]" : ""} rounded px-0.5 cursor-pointer transition-all inline`}
              onMouseEnter={() => setSelected(i)}
              onMouseLeave={() => setSelected(null)}
            >
              {s.text}{" "}
            </span>
          ))}
        </div>
      </div>

      <div className="bg-white rounded-2xl p-6 border border-[var(--card-border)] shadow-sm">
        <h4 className="text-xs font-medium text-[var(--muted)] mb-3">
          Per-sentence breakdown
        </h4>
        <div className="space-y-1.5 max-h-[220px] overflow-y-auto">
          {sentenceScores.map((s, i) => (
            <div
              key={i}
              className={`flex items-center gap-3 p-2.5 rounded-xl text-xs transition-all cursor-default ${selected === i ? "bg-[var(--background)] ring-1 ring-[var(--accent)]" : "hover:bg-[var(--background)]"}`}
              onMouseEnter={() => setSelected(i)}
              onMouseLeave={() => setSelected(null)}
            >
              <span
                className={`shrink-0 px-2 py-0.5 rounded-full border text-[10px] font-medium ${getLabelStyle(s.aiScore)}`}
              >
                {s.label}
              </span>
              <span className="text-[var(--foreground)] truncate flex-1 min-w-0">
                {s.text}
              </span>
              <span className="shrink-0 font-mono text-[var(--muted)] tabular-nums">
                {s.aiScore.toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
