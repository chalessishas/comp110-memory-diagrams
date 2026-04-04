import type { MasteryLevel } from "@/types";

interface AttemptRecord {
  is_correct: boolean;
  answered_at: string;
}

export function calculateMastery(attempts: AttemptRecord[]): { level: MasteryLevel; rate: number; total: number } {
  if (attempts.length === 0) return { level: "untested", rate: 0, total: 0 };

  const recent = [...attempts]
    .sort((a, b) => new Date(b.answered_at).getTime() - new Date(a.answered_at).getTime())
    .slice(0, 10);

  const correct = recent.filter((a) => a.is_correct).length;
  const rate = correct / recent.length;

  const level: MasteryLevel = rate > 0.8 ? "mastered" : rate >= 0.4 ? "reviewing" : "weak";

  return { level, rate, total: attempts.length };
}

export const masteryColors: Record<MasteryLevel, string> = {
  mastered: "var(--accent)",
  reviewing: "#6c6c66",
  weak: "#b6b6af",
  untested: "#e3e3dc",
};

export const masteryLabels: Record<MasteryLevel, string> = {
  mastered: "Mastered",
  reviewing: "Needs Review",
  weak: "Weak",
  untested: "Untested",
};
