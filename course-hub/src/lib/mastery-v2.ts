import type { MasteryLevelV2 } from "@/types";

export interface MasteryStats {
  currentLevel: MasteryLevelV2;
  timesTested: number;
  timesCorrect: number;
  timesNonMcq: number;
  timesNonMcqCorrect: number;
  hasExternalPractice: boolean;
  hasNonMcqCorrect: boolean;
  hasCrossConceptCorrect: boolean;
  hasTransferCorrect: boolean;
  hasTeachingChallengePass: boolean;
  fsrsStability: number;
  fsrsRetrievability: number;
  firstContactAt: Date;
  levelReachedAt: Date;
  recentAccuracy: number; // last 5 attempts
  recentCount: number;
  hasDownstreamDependents: boolean;
}

export interface EvaluationResult {
  newLevel: MasteryLevelV2;
  changed: boolean;
  reason: string;
  uiMessage: string; // positive framing, never "you forgot"
  uiMessageZh: string;
}

export function evaluateLevel(stats: MasteryStats, hasCompletedLesson: boolean): EvaluationResult {
  const current = stats.currentLevel;
  const now = new Date();

  // ─── Downgrade checks (gentle) ───

  if (current === "mastered" && stats.fsrsRetrievability < 0.70) {
    return {
      newLevel: "proficient",
      changed: true,
      reason: "FSRS retrievability dropped below 0.70",
      uiMessage: "Ready for a quick refresher on this topic",
      uiMessageZh: "可以复习巩固一下这个知识点",
    };
  }

  if (current === "proficient" && stats.fsrsRetrievability < 0.70) {
    return {
      newLevel: "practiced",
      changed: true,
      reason: "FSRS retrievability dropped below 0.70",
      uiMessage: "This topic is ready to be strengthened",
      uiMessageZh: "这个知识点准备好巩固了",
    };
  }

  if (current === "practiced" && stats.recentAccuracy < 0.50 && stats.recentCount >= 3) {
    return {
      newLevel: "exposed",
      changed: true,
      reason: "Recent accuracy below 50% over 3+ attempts",
      uiMessage: "Consider revisiting this lesson",
      uiMessageZh: "建议重新看一遍这节课",
    };
  }

  // ─── Upgrade checks ───

  if (current === "unseen" && hasCompletedLesson) {
    return {
      newLevel: "exposed",
      changed: true,
      reason: "Completed lesson containing this concept",
      uiMessage: "New concept unlocked",
      uiMessageZh: "新概念已解锁",
    };
  }

  if (current === "exposed") {
    if (
      stats.timesTested >= 5 &&
      stats.recentAccuracy >= 0.70 &&
      stats.hasExternalPractice
    ) {
      return {
        newLevel: "practiced",
        changed: true,
        reason: "5+ attempts, 70%+ accuracy, external practice done",
        uiMessage: "Making progress — keep practicing",
        uiMessageZh: "进步明显，继续练习",
      };
    }
  }

  if (current === "practiced") {
    const daysSinceFirstContact = (now.getTime() - stats.firstContactAt.getTime()) / (1000 * 60 * 60 * 24);

    // Check all conditions for Level 3
    const accuracyOk = stats.recentAccuracy >= 0.85;
    const nonMcqOk = stats.hasNonMcqCorrect;
    const stabilityOk = stats.fsrsStability >= 7;
    const sleepOk = daysSinceFirstContact >= 3;
    // Cross-concept gate: if this KP has child KPs in the outline, the student must
    // demonstrate understanding across concepts before reaching proficient. The gate is
    // skipped for leaf nodes (no downstream dependents) since there is nothing to cross-reference.
    const crossConceptOk = stats.hasCrossConceptCorrect || !stats.hasDownstreamDependents;

    if (accuracyOk && nonMcqOk && stabilityOk && sleepOk && crossConceptOk) {
      return {
        newLevel: "proficient",
        changed: true,
        reason: "All proficiency criteria met",
        uiMessage: "Proficient — you can apply this confidently",
        uiMessageZh: "已熟练——可以自信地运用了",
      };
    }
  }

  if (current === "proficient") {
    const daysSinceLevel3 = (now.getTime() - stats.levelReachedAt.getTime()) / (1000 * 60 * 60 * 24);

    if (
      daysSinceLevel3 >= 21 &&
      stats.hasTeachingChallengePass &&
      stats.hasTransferCorrect
    ) {
      return {
        newLevel: "mastered",
        changed: true,
        reason: "21+ days at proficient, teaching challenge passed, transfer test passed",
        uiMessage: "Mastered — you can teach this to others",
        uiMessageZh: "已精通——你可以教别人了",
      };
    }
  }

  // No change
  return {
    newLevel: current,
    changed: false,
    reason: "No level change criteria met",
    uiMessage: "",
    uiMessageZh: "",
  };
}

// Anti-cramming check
export function shouldBlockUpgrade(
  context: "practice" | "review" | "learn_checkpoint",
  conceptId: string,
  attemptsInLastHour: number
): { blocked: boolean; message: string; messageZh: string } {
  if (context === "review") {
    // FSRS-driven reviews are never blocked
    return { blocked: false, message: "", messageZh: "" };
  }

  if (context === "learn_checkpoint") {
    // Max 3 attempts per checkpoint (original + 2 variants)
    if (attemptsInLastHour > 3) {
      return {
        blocked: true,
        message: "Maximum attempts reached for this checkpoint",
        messageZh: "这个检查点已达最大尝试次数",
      };
    }
    return { blocked: false, message: "", messageZh: "" };
  }

  // Practice: block after 10 attempts/hour
  if (attemptsInLastHour > 10) {
    return {
      blocked: true,
      message: "You've practiced this enough for today. Come back tomorrow for better retention.",
      messageZh: "今天这个知识点练够了，明天再来效果更好。",
    };
  }

  return { blocked: false, message: "", messageZh: "" };
}

// Visual styling for levels
export const levelConfig: Record<MasteryLevelV2, {
  color: string;
  bgColor: string;
  label: string;
  labelZh: string;
  size: number; // relative size for knowledge tree nodes
}> = {
  unseen: {
    color: "var(--border)",
    bgColor: "transparent",
    label: "Not started",
    labelZh: "未接触",
    size: 20,
  },
  exposed: {
    color: "var(--danger)",
    bgColor: "rgba(220, 38, 38, 0.1)",
    label: "Seen",
    labelZh: "见过",
    size: 28,
  },
  practiced: {
    color: "var(--warning)",
    bgColor: "rgba(217, 119, 6, 0.1)",
    label: "Practiced",
    labelZh: "能做对",
    size: 36,
  },
  proficient: {
    color: "var(--success)",
    bgColor: "rgba(5, 150, 105, 0.1)",
    label: "Proficient",
    labelZh: "熟练",
    size: 44,
  },
  mastered: {
    color: "var(--success)",
    bgColor: "rgba(5, 150, 105, 0.15)",
    label: "Mastered",
    labelZh: "精通",
    size: 52,
  },
};
