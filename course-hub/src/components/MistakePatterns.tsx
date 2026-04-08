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
    <div className="mb-6 p-5 rounded-[20px]" style={{ backgroundColor: "var(--bg-muted)" }}>
      <div className="flex items-center gap-2 mb-4">
        <TrendingDown size={16} style={{ color: "var(--danger)" }} />
        <h3 className="text-sm font-medium" style={{ color: "var(--text-primary)" }}>
          {isZh ? "\u8584\u5f31\u77e5\u8bc6\u70b9" : "Weak Spots"}
        </h3>
      </div>

      <div className="space-y-3">
        {patterns.map((p) => {
          const pct = Math.round(p.error_rate * 100);
          const barColor = pct >= 60 ? "var(--danger)" : pct >= 40 ? "var(--warning)" : "var(--accent)";

          return (
            <div key={p.kp_id} className="flex items-center gap-3">
              <div className="flex-1 min-w-0">
                <div className="flex items-center justify-between mb-1.5">
                  <p className="text-xs truncate font-medium" style={{ color: "var(--text-primary)" }}>
                    {p.kp_title}
                  </p>
                  <div className="flex items-center gap-1.5 shrink-0 ml-2">
                    {pct >= 50 && <AlertTriangle size={10} style={{ color: "var(--danger)" }} />}
                    <span className="text-[10px]" style={{ color: pct >= 50 ? "var(--danger)" : "var(--text-muted)", fontFamily: "inherit" }}>
                      {p.wrong_attempts}/{p.total_attempts}
                    </span>
                  </div>
                </div>
                <div className="ui-progress-track">
                  <div
                    className="ui-progress-bar"
                    style={{ width: `${pct}%`, backgroundColor: barColor }}
                  />
                </div>
              </div>
              <span className="text-xs font-medium w-10 text-right" style={{ color: barColor }}>
                {pct}%
              </span>
            </div>
          );
        })}
      </div>

      <p className="text-[10px] mt-4" style={{ color: "var(--text-muted)" }}>
        {isZh ? "\u9519\u8bef\u7387 = \u7b54\u9519\u6b21\u6570 / \u603b\u7b54\u9898\u6b21\u6570\uff0c\u6309\u77e5\u8bc6\u70b9\u805a\u5408" : "Error rate = wrong / total attempts, grouped by knowledge point"}
      </p>
    </div>
  );
}
