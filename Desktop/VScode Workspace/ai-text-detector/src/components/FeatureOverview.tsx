"use client";

import type { AnalysisResult, FeatureScore } from "@/lib/analysis";

interface Props {
  result: AnalysisResult;
}

function ScoreBar({ score }: { score: number }) {
  const color =
    score > 0.7 ? "bg-red-400" : score > 0.3 ? "bg-amber-400" : "bg-emerald-400";
  return (
    <div className="h-1.5 rounded-full bg-gray-100 mt-1.5">
      <div
        style={{ width: `${score * 100}%` }}
        className={`h-full rounded-full ${color} transition-all`}
      />
    </div>
  );
}

function FeatureCard({ feature }: { feature: FeatureScore }) {
  const label =
    feature.score > 0.7
      ? "AI-like"
      : feature.score > 0.3
        ? "Mixed"
        : "Human-like";
  const labelColor =
    feature.score > 0.7
      ? "text-red-600"
      : feature.score > 0.3
        ? "text-amber-600"
        : "text-emerald-600";

  return (
    <div className="bg-[var(--background)] rounded-xl p-3">
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium text-[var(--foreground)]">
          {feature.name}
        </span>
        <span className={`text-[10px] font-medium ${labelColor}`}>
          {label}
        </span>
      </div>
      <ScoreBar score={feature.score} />
      <div className="flex justify-between mt-2 text-[10px] text-[var(--muted)]">
        <span>Raw: {feature.raw.toFixed(2)}</span>
        <span>
          H: {feature.humanRef} | AI: {feature.aiRef}
        </span>
      </div>
    </div>
  );
}

export default function FeatureOverview({ result }: Props) {
  return (
    <div className="space-y-4">
      <div className="bg-white rounded-2xl p-6 border border-[var(--card-border)] shadow-sm">
        <h3 className="text-sm font-semibold text-[var(--foreground)] mb-1">
          Feature Breakdown
        </h3>
        <p className="text-xs text-[var(--muted)] mb-4">
          Each feature normalized 0-1 (0 = human-like, 1 = AI-like), weighted
          for overall score.
        </p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
          {result.featureScores.map((f) => (
            <FeatureCard key={f.name} feature={f} />
          ))}
        </div>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-white rounded-2xl p-5 border border-[var(--card-border)] shadow-sm">
          <h4 className="text-xs font-semibold text-[var(--foreground)] mb-3">
            Vocabulary
          </h4>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[var(--muted)]">Type-Token Ratio</span>
              <span className="font-medium">
                {result.vocabulary.ttr.toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--muted)]">Hapax Ratio</span>
              <span className="font-medium">
                {result.vocabulary.hapaxRatio.toFixed(3)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--muted)]">Unique / Total</span>
              <span className="font-medium">
                {result.vocabulary.uniqueWords} / {result.vocabulary.totalWords}
              </span>
            </div>
          </div>
        </div>
        <div className="bg-white rounded-2xl p-5 border border-[var(--card-border)] shadow-sm">
          <h4 className="text-xs font-semibold text-[var(--foreground)] mb-3">
            Sentence Length
          </h4>
          <div className="space-y-2 text-xs">
            <div className="flex justify-between">
              <span className="text-[var(--muted)]">Mean</span>
              <span className="font-medium">
                {result.sentenceLength.mean.toFixed(1)} words
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--muted)]">Std Dev</span>
              <span className="font-medium">
                {result.sentenceLength.std.toFixed(1)}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-[var(--muted)]">Burstiness CV</span>
              <span className="font-medium">
                {result.burstiness.lengthCV.toFixed(3)}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
