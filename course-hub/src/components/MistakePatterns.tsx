"use client";

import { useEffect, useState } from "react";
import { AlertTriangle, TrendingDown } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface MistakePattern {
  kp_id: string;
  kp_title: string;
  total_attempts: number;
  wrong_attempts: number;
  error_rate: number;
  unique_questions: number;
  last_wrong_at: string | null;
}

export function MistakePatterns({ courseId }: { courseId: string }) {
  const { locale } = useI18n();
  const isZh = locale === "zh";
  const [patterns, setPatterns] = useState<MistakePattern[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`/api/courses/${courseId}/mistake-patterns`)
      .then(r => r.json())
      .then((data: MistakePattern[]) => {
        setPatterns(Array.isArray(data) ? data.slice(0, 5) : []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, [courseId]);

  if (loading || patterns.length === 0) return null;

  return (
    <div className="mb-6 p-4 rounded-xl" style={{ backgroundColor: "rgba(239, 68, 68, 0.04)", border: "1px solid rgba(239, 68, 68, 0.15)" }}>
      <div className="flex items-center gap-2 mb-3">
        <TrendingDown size={16} style={{ color: "var(--danger)" }} />
        <h3 className="text-sm font-semibold" style={{ color: "var(--danger)" }}>
          {isZh ? "薄弱知识点" : "Weak Spots"}
        </h3>
      </div>

      <div className="space-y-2">
        {patterns.map((p) => {
          const pct = Math.round(p.error_rate * 100);
          const barColor = pct >= 60 ? "var(--danger)" : pct >= 40 ? "var(--warning)" : "var(--accent)";

          return (
            <div key={p.kp_id} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1">
                  <p className="text-xs truncate font-medium" style={{ color: "var(--text-primary)" }}>
                    {p.kp_title}
                  </p>
                  <div className="flex items-center gap-1 shrink-0 ml-2">
                    {pct >= 50 && <AlertTriangle size={10} style={{ color: "var(--danger)" }} />}
                    <span className="text-[10px] font-mono" style={{ color: pct >= 50 ? "var(--danger)" : "var(--text-muted)" }}>
                      {p.wrong_attempts}/{p.total_attempts}
                    </span>
                  </div>
                </div>
                <div className="h-1.5 rounded-full overflow-hidden" style={{ backgroundColor: "var(--bg-muted)" }}>
                  <div
                    className="h-full rounded-full transition-all"
                    style={{ width: `${pct}%`, backgroundColor: barColor }}
                  />
                </div>
              </div>
              <span className="text-xs font-bold w-10 text-right" style={{ color: barColor }}>
                {pct}%
              </span>
            </div>
          );
        })}
      </div>

      <p className="text-[10px] mt-3" style={{ color: "var(--text-muted)" }}>
        {isZh ? "错误率 = 答错次数 / 总答题次数，按知识点聚合" : "Error rate = wrong / total attempts, grouped by knowledge point"}
      </p>
    </div>
  );
}
