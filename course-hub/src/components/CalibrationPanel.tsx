"use client";

import { Brain } from "lucide-react";
import { useI18n } from "@/lib/i18n";

interface ConfStat {
  lvl: number;
  total: number;
  accuracy: number | null;
}

interface CalibrationPanelProps {
  confStats: ConfStat[];
  totalRated: number;
  isCalibrated: boolean;
  isOverconfident: boolean;
}

export function CalibrationPanel({ confStats, totalRated, isCalibrated, isOverconfident }: CalibrationPanelProps) {
  const { t } = useI18n();

  const labels: Record<number, string> = {
    1: t("calibration.guessing"),
    2: t("calibration.unsure"),
    3: t("calibration.confident"),
  };

  return (
    <div className="ui-panel p-5">
      <div className="flex items-center gap-2 mb-4">
        <Brain size={16} style={{ color: "var(--accent)" }} />
        <span className="text-sm font-medium">{t("calibration.title")}</span>
        {isCalibrated && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded-lg font-medium" style={{ backgroundColor: "var(--success)", color: "white" }}>
            {t("calibration.wellCalibrated")}
          </span>
        )}
        {isOverconfident && (
          <span className="ml-auto text-xs px-2 py-0.5 rounded-lg font-medium" style={{ backgroundColor: "var(--warning)", color: "white" }}>
            {t("calibration.overconfident")}
          </span>
        )}
      </div>
      <div className="space-y-2.5">
        {confStats.map(({ lvl, total, accuracy }) => {
          const emoji = lvl === 1 ? "🤔" : lvl === 2 ? "🙂" : "😎";
          const pct = accuracy !== null ? Math.round(accuracy * 100) : null;
          const color = pct === null ? "var(--text-muted)"
            : pct >= 75 ? "var(--success)" : pct >= 50 ? "var(--warning)" : "var(--danger)";
          return (
            <div key={lvl} className="flex items-center gap-3">
              <span className="w-5 text-center text-sm">{emoji}</span>
              <span className="text-xs w-16" style={{ color: "var(--text-secondary)" }}>{labels[lvl]}</span>
              <div className="flex-1 ui-progress-track">
                <div className="ui-progress-bar" style={{ width: `${pct ?? 0}%`, backgroundColor: color }} />
              </div>
              <span className="text-xs w-20 text-right" style={{ color }}>
                {pct !== null ? `${pct}% (${total})` : "—"}
              </span>
            </div>
          );
        })}
      </div>
      <p className="text-[10px] mt-3" style={{ color: "var(--text-muted)" }}>
        {t("calibration.footer")} {totalRated} {t("calibration.ratedAttempts")}.
      </p>
    </div>
  );
}
