// ═══════════════════════════════════════════════════════════════
// Evaluation Rubrics: 8 dimensions × 5-point scale
// ═══════════════════════════════════════════════════════════════
//
// Each dimension has machine-checkable criteria (automated)
// and human-judgment criteria (requires manual review).
// Score: 1-5 per dimension, weighted total out of 100.

import type { BloomLevel, TestKnowledgePoint } from "./test-data";

export interface DimensionScore {
  dimension: string;
  score: number;       // 1-5
  maxScore: 5;
  weight: number;      // contribution to total (sums to 100)
  details: string;     // explanation of score
  automated: boolean;  // true = machine-scored, false = needs human review
}

export interface QuestionEvaluation {
  testKpId: string;
  questionIndex: number;
  questionType: string;
  stem: string;
  dimensions: DimensionScore[];
  totalScore: number;      // weighted 0-100
  flags: string[];         // critical issues
}

export interface BenchmarkReport {
  timestamp: string;
  totalKPs: number;
  totalQuestions: number;
  overallScore: number;    // 0-100 average across all questions
  bySubject: Record<string, { avgScore: number; questionCount: number }>;
  byDimension: Record<string, { avgScore: number; distribution: number[] }>; // distribution[0]=count of 1s, etc.
  criticalFlags: string[];
  questions: QuestionEvaluation[];
}

// ─── Dimension Definitions ───────────────────────────────────

export const DIMENSIONS = {
  // D1: Is the answer factually correct?
  answerCorrectness: {
    name: "Answer Correctness",
    nameZh: "答案正确性",
    weight: 25,
    automated: true,
    rubric: {
      5: "Answer exactly matches ground truth; all factual claims verified",
      4: "Answer correct but minor wording difference from ground truth",
      3: "Answer mostly correct, one minor inaccuracy that doesn't change meaning",
      2: "Answer partially correct — major fact is wrong but core concept is right",
      1: "Answer is incorrect — contradicts ground truth",
    },
  },

  // D2: Are MCQ distractors plausible and based on real misconceptions?
  distractorQuality: {
    name: "Distractor Quality",
    nameZh: "干扰项质量",
    weight: 15,
    automated: false, // requires human judgment
    rubric: {
      5: "All distractors target real student misconceptions from ground truth list",
      4: "3/3 distractors plausible, at least 2 target known misconceptions",
      3: "Distractors plausible but generic, don't target specific misconceptions",
      2: "1+ distractor is obviously wrong (no student would choose it)",
      1: "Distractors are nonsensical or contain the answer",
    },
  },

  // D3: Does the question test the intended knowledge point?
  kpAlignment: {
    name: "KP Alignment",
    nameZh: "知识点匹配度",
    weight: 15,
    automated: true,
    rubric: {
      5: "Question directly tests the core concept of the KP, uses key terms",
      4: "Question tests the KP but could also apply to a related KP",
      3: "Question is tangentially related to KP — tests a prerequisite or extension",
      2: "Question is about the same subject but a different KP",
      1: "Question is unrelated to the intended KP",
    },
  },

  // D4: Does the stated difficulty match actual cognitive demand?
  difficultyCal: {
    name: "Difficulty Calibration",
    nameZh: "难度校准",
    weight: 10,
    automated: true,
    rubric: {
      5: "Stated difficulty within ±0 of expected range",
      4: "Stated difficulty within ±1 of expected range",
      3: "Stated difficulty within ±2 of expected range",
      2: "Stated difficulty off by 3+ or all questions same difficulty",
      1: "Difficulty rating is clearly backwards (hard question rated 1, easy rated 5)",
    },
  },

  // D5: What Bloom's level does the question actually test?
  bloomLevel: {
    name: "Bloom's Taxonomy Level",
    nameZh: "Bloom 认知层级",
    weight: 15,
    automated: false,
    rubric: {
      5: "Question tests the expected Bloom level(s); set includes higher-order questions",
      4: "At least one question reaches expected Bloom level; others are one level below",
      3: "All questions are Remember/Understand — no Apply or above",
      2: "Questions only test factual recall despite KP requiring application/analysis",
      1: "Questions test a lower cognitive level than the topic warrants (e.g., recall formula for a problem-solving KP)",
    },
  },

  // D6: Is the question stem clear and unambiguous?
  stemClarity: {
    name: "Stem Clarity",
    nameZh: "题干清晰度",
    weight: 10,
    automated: false,
    rubric: {
      5: "Stem is clear, concise, self-contained, no ambiguity",
      4: "Stem is clear but could be slightly more concise",
      3: "Stem has minor ambiguity but intent is understandable",
      2: "Stem is confusing — multiple valid interpretations",
      1: "Stem is incomprehensible, has grammatical errors, or contradicts itself",
    },
  },

  // D7: Is the explanation educational and helps learning?
  explanationQuality: {
    name: "Explanation Quality",
    nameZh: "解释质量",
    weight: 5,
    automated: false,
    rubric: {
      5: "Explanation teaches WHY the answer is correct, addresses common misconception",
      4: "Explanation is correct and clear but doesn't address misconceptions",
      3: "Explanation is just the answer restated differently",
      2: "Explanation is vague or adds no insight beyond the answer",
      1: "No explanation provided, or explanation is wrong",
    },
  },

  // D8: Does the question set cover different types and angles?
  diversity: {
    name: "Type & Angle Diversity",
    nameZh: "题型多样性",
    weight: 5,
    automated: true,
    rubric: {
      5: "≥3 question types used, questions test different aspects of the KP",
      4: "2 question types, questions test different aspects",
      3: "2 question types but questions test the same aspect",
      2: "All same type, test different aspects",
      1: "All same type, all test the same thing",
    },
  },
} as const;

export type DimensionKey = keyof typeof DIMENSIONS;

// ─── Automated Scoring Functions ─────────────────────────────

export function scoreAnswerCorrectness(
  aiAnswer: string,
  groundTruthFacts: string[],
  knownTraps: string[],
): DimensionScore {
  const lower = aiAnswer.toLowerCase();

  // Check if answer falls into known AI traps
  const trappedOn = knownTraps.filter(trap =>
    trap.toLowerCase().split(" ").some(word =>
      word.length > 4 && lower.includes(word.toLowerCase())
    )
  );

  // Check how many ground truth facts are consistent with the answer
  const factKeywords = groundTruthFacts.map(f => {
    const words = f.toLowerCase().split(/\s+/).filter(w => w.length > 3);
    return { fact: f, words };
  });

  const matchedFacts = factKeywords.filter(({ words }) =>
    words.some(w => lower.includes(w))
  );

  const matchRatio = factKeywords.length > 0
    ? matchedFacts.length / Math.min(factKeywords.length, 3) // only check top 3 relevant facts
    : 0;

  let score: number;
  let details: string;

  if (trappedOn.length > 0) {
    score = 2;
    details = `Answer may contain known AI error: ${trappedOn[0]}`;
  } else if (matchRatio >= 0.8) {
    score = 5;
    details = `Answer aligns with ${matchedFacts.length} ground truth facts`;
  } else if (matchRatio >= 0.5) {
    score = 4;
    details = `Answer partially aligns (${matchedFacts.length}/${Math.min(factKeywords.length, 3)} facts matched)`;
  } else {
    score = 3;
    details = `Low fact overlap — needs human verification`;
  }

  return {
    dimension: "answerCorrectness",
    score,
    maxScore: 5,
    weight: DIMENSIONS.answerCorrectness.weight,
    details,
    automated: true,
  };
}

export function scoreKpAlignment(
  stem: string,
  keyTerms: string[],
  kpTitle: string,
): DimensionScore {
  const lower = stem.toLowerCase();
  const titleWords = kpTitle.toLowerCase().split(/\s+/).filter(w => w.length > 3);
  const termMatches = keyTerms.filter(t => lower.includes(t.toLowerCase()));
  const titleMatches = titleWords.filter(w => lower.includes(w));

  const termRatio = keyTerms.length > 0 ? termMatches.length / keyTerms.length : 0;
  const titleMatch = titleMatches.length > 0;

  let score: number;
  if (termRatio >= 0.4 || (titleMatch && termRatio >= 0.2)) {
    score = 5;
  } else if (termRatio >= 0.2 || titleMatch) {
    score = 4;
  } else if (termMatches.length >= 1) {
    score = 3;
  } else {
    score = 2;
  }

  return {
    dimension: "kpAlignment",
    score,
    maxScore: 5,
    weight: DIMENSIONS.kpAlignment.weight,
    details: `Key terms found: [${termMatches.join(", ")}] (${termMatches.length}/${keyTerms.length})`,
    automated: true,
  };
}

export function scoreDifficultyCalibration(
  aiDifficulty: number,
  expectedDifficulty: number,
): DimensionScore {
  const diff = Math.abs(aiDifficulty - expectedDifficulty);
  const score = diff === 0 ? 5 : diff === 1 ? 4 : diff === 2 ? 3 : 2;

  return {
    dimension: "difficultyCal",
    score,
    maxScore: 5,
    weight: DIMENSIONS.difficultyCal.weight,
    details: `AI: ${aiDifficulty}, Expected: ${expectedDifficulty}, Δ=${diff}`,
    automated: true,
  };
}

export function scoreDiversity(
  questions: { type: string; stem: string }[],
): DimensionScore {
  const types = new Set(questions.map(q => q.type));
  const typeCount = types.size;

  // Simple angle diversity: check if stems have different key phrases
  const stems = questions.map(q => q.stem.toLowerCase());
  const uniqueStarts = new Set(stems.map(s => s.slice(0, 30)));
  const angleDiv = uniqueStarts.size / Math.max(stems.length, 1);

  let score: number;
  if (typeCount >= 3 && angleDiv >= 0.7) score = 5;
  else if (typeCount >= 2 && angleDiv >= 0.5) score = 4;
  else if (typeCount >= 2) score = 3;
  else if (angleDiv >= 0.7) score = 2;
  else score = 1;

  return {
    dimension: "diversity",
    score,
    maxScore: 5,
    weight: DIMENSIONS.diversity.weight,
    details: `${typeCount} types: [${[...types].join(", ")}], angle diversity: ${(angleDiv * 100).toFixed(0)}%`,
    automated: true,
  };
}

// ─── Bloom's Level Detection (heuristic) ─────────────────────

const BLOOM_INDICATORS: Record<BloomLevel, string[]> = {
  remember: [
    "define", "list", "name", "state", "recall", "identify", "what is", "which of the following",
    "列举", "说出", "写出", "指出", "定义", "是什么", "哪一个", "以下哪项", "选出",
  ],
  understand: [
    "explain", "describe", "summarize", "compare", "contrast", "interpret", "why",
    "解释", "描述", "概括", "说明", "阐述", "为什么", "区别", "含义", "理解",
  ],
  apply: [
    "calculate", "compute", "solve", "determine", "find", "evaluate the integral", "use", "apply",
    "计算", "求解", "运用", "应用", "求出", "利用", "根据", "代入", "演示",
  ],
  analyze: [
    "analyze", "distinguish", "compare and contrast", "what would happen if", "why does", "relationship between",
    "分析", "比较", "对比", "区分", "推断", "关系", "异同", "如果…会", "原因是",
  ],
  evaluate: [
    "justify", "critique", "assess", "which approach is best", "argue", "defend",
    "评价", "评估", "论证", "判断", "辩护", "哪种方法更", "合理性", "批判", "优劣",
  ],
  create: [
    "design", "construct", "propose", "develop", "create", "formulate",
    "设计", "构造", "提出", "拟定", "创造", "编写", "制定", "规划",
  ],
};

export function detectBloomLevel(stem: string): BloomLevel {
  const lower = stem.toLowerCase();

  // Check from highest to lowest (prefer higher classification)
  for (const level of ["create", "evaluate", "analyze", "apply", "understand", "remember"] as BloomLevel[]) {
    if (BLOOM_INDICATORS[level].some(ind => lower.includes(ind))) {
      return level;
    }
  }
  return "remember"; // default if no indicators found
}

export function scoreBloomLevel(
  detectedLevel: BloomLevel,
  expectedLevels: BloomLevel[],
): DimensionScore {
  const BLOOM_ORDER: BloomLevel[] = ["remember", "understand", "apply", "analyze", "evaluate", "create"];
  const detectedIdx = BLOOM_ORDER.indexOf(detectedLevel);
  const expectedMaxIdx = Math.max(...expectedLevels.map(l => BLOOM_ORDER.indexOf(l)));
  const expectedMinIdx = Math.min(...expectedLevels.map(l => BLOOM_ORDER.indexOf(l)));

  let score: number;
  if (detectedIdx >= expectedMinIdx && detectedIdx <= expectedMaxIdx) {
    score = 5;
  } else if (detectedIdx === expectedMinIdx - 1) {
    score = 4;
  } else if (detectedIdx < expectedMinIdx) {
    score = 3;
  } else {
    score = 4; // above expected = still good
  }

  return {
    dimension: "bloomLevel",
    score,
    maxScore: 5,
    weight: DIMENSIONS.bloomLevel.weight,
    details: `Detected: ${detectedLevel}, Expected: [${expectedLevels.join(", ")}]`,
    automated: false, // heuristic — should be verified by human
  };
}

// ─── Placeholder scores for human-review dimensions ──────────

export function placeholderScore(dimension: DimensionKey): DimensionScore {
  return {
    dimension,
    score: 0, // 0 = not yet scored
    maxScore: 5,
    weight: DIMENSIONS[dimension].weight,
    details: "Awaiting human review",
    automated: false,
  };
}

// ─── Compute weighted total ──────────────────────────────────

export function computeWeightedTotal(dimensions: DimensionScore[]): number {
  const scored = dimensions.filter(d => d.score > 0);
  if (scored.length === 0) return 0;

  const totalWeight = scored.reduce((sum, d) => sum + d.weight, 0);
  const weightedSum = scored.reduce((sum, d) => sum + (d.score / d.maxScore) * d.weight, 0);

  return totalWeight > 0 ? (weightedSum / totalWeight) * 100 : 0;
}
