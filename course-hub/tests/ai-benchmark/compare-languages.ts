#!/usr/bin/env npx tsx
// ═══════════════════════════════════════════════════════════════
// Bilingual Quality Comparison Runner
// ═══════════════════════════════════════════════════════════════
//
// For STEM subjects, tests whether a model generates better content
// in English vs Chinese. The "optimal generation language" can then
// be used as default, with translation to the user's native language.
//
// Insight: Many models have stronger math reasoning in English
// (training data bias). If EN math score >> ZH math score,
// generate in EN then translate — translation quality loss is
// smaller than the direct generation quality gap.
//
// Usage:
//   DASHSCOPE_API_KEY=xxx npx tsx tests/ai-benchmark/compare-languages.ts
//   --model qwen3.5-plus  (required: which model to test)
//   --subject calculus     (optional: one subject, default: all STEM)

import { TEST_SUBJECTS, SUBJECT_LABELS, type Subject, type TestKnowledgePoint } from "./test-data";
import { MODELS, createModelGenerator, type ModelConfig } from "./models";
import {
  DIMENSIONS,
  scoreAnswerCorrectness,
  scoreKpAlignment,
  scoreDifficultyCalibration,
  scoreDiversity,
  scoreBloomLevel,
  detectBloomLevel,
  computeWeightedTotal,
  type DimensionScore,
} from "./rubrics";

// ─── Bilingual KP pairs (same topic, EN + ZH prompts) ─────────

interface BilingualKP {
  id: string;
  subject: Subject;
  en: { courseTitle: string; title: string; content: string };
  zh: { courseTitle: string; title: string; content: string };
  groundTruth: TestKnowledgePoint["groundTruth"];
  knownAITraps: string[];
}

// STEM subjects where language quality gap matters most
const BILINGUAL_KPS: BilingualKP[] = [
  {
    id: "bi-calc-001",
    subject: "calculus",
    en: {
      courseTitle: "Calculus II",
      title: "Integration by Parts",
      content: "Technique for integrating products of functions using ∫u dv = uv - ∫v du",
    },
    zh: {
      courseTitle: "高等数学（下）",
      title: "分部积分法",
      content: "利用公式 ∫u dv = uv - ∫v du 计算两个函数乘积的积分",
    },
    groundTruth: {
      correctFacts: [
        "∫u dv = uv - ∫v du",
        "LIATE rule for choosing u",
        "∫x·eˣ dx = x·eˣ - eˣ + C",
        "May require multiple applications",
      ],
      commonMisconceptions: [
        "Confusing u vs dv assignment",
        "Forgetting the minus sign",
        "IBP always simplifies (sometimes loops)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["integration by parts", "分部积分", "LIATE", "uv"],
    },
    knownAITraps: ["AI may state LIATE as strict rule"],
  },
  {
    id: "bi-calc-002",
    subject: "calculus",
    en: {
      courseTitle: "Calculus II",
      title: "Taylor Series and Convergence",
      content: "Taylor/Maclaurin series expansion, radius of convergence, common series",
    },
    zh: {
      courseTitle: "高等数学（下）",
      title: "泰勒级数与收敛性",
      content: "泰勒/麦克劳林级数展开，收敛半径，常见函数的级数展开",
    },
    groundTruth: {
      correctFacts: [
        "f(x) = Σ f⁽ⁿ⁾(a)/n! · (x-a)ⁿ",
        "Maclaurin series: Taylor series at a = 0",
        "eˣ = Σ xⁿ/n! (converges for all x)",
        "Ratio test for convergence: |aₙ₊₁/aₙ| < 1",
      ],
      commonMisconceptions: [
        "Taylor series always converges everywhere",
        "More terms always means more accurate",
      ],
      expectedDifficulty: 4,
      bloomLevels: ["apply", "analyze"],
      keyTerms: ["Taylor series", "泰勒级数", "convergence", "收敛", "radius"],
    },
    knownAITraps: ["AI may say all Taylor series converge everywhere"],
  },
  {
    id: "bi-phys-001",
    subject: "physics",
    en: {
      courseTitle: "General Physics",
      title: "Newton's Laws of Motion",
      content: "Three laws of motion, free body diagrams, applications to connected systems",
    },
    zh: {
      courseTitle: "大学物理",
      title: "牛顿运动定律",
      content: "三大运动定律、受力分析图、连接体系统的应用",
    },
    groundTruth: {
      correctFacts: [
        "F = ma (Newton's second law)",
        "Action-reaction pairs act on different objects",
        "Inertial reference frames required for Newton's laws",
      ],
      commonMisconceptions: [
        "Heavier objects fall faster",
        "Force is needed to maintain velocity",
        "Action-reaction cancel each other",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["understand", "apply"],
      keyTerms: ["Newton", "牛顿", "F=ma", "inertia", "惯性"],
    },
    knownAITraps: ["AI may not emphasize inertial frame requirement"],
  },
  {
    id: "bi-phys-002",
    subject: "physics",
    en: {
      courseTitle: "General Physics",
      title: "Thermodynamics: Entropy and Second Law",
      content: "Entropy, Carnot cycle, second law statements (Clausius, Kelvin-Planck)",
    },
    zh: {
      courseTitle: "大学物理",
      title: "热力学：熵与热力学第二定律",
      content: "熵的概念、卡诺循环、热力学第二定律的两种表述（克劳修斯、开尔文）",
    },
    groundTruth: {
      correctFacts: [
        "ΔS ≥ 0 for isolated system (entropy never decreases)",
        "Carnot efficiency: η = 1 - Tc/Th",
        "Clausius: heat cannot spontaneously flow from cold to hot",
        "Kelvin-Planck: no engine can convert heat entirely to work",
      ],
      commonMisconceptions: [
        "Entropy always increases (only in isolated systems)",
        "Perfect efficiency is theoretically possible",
        "Entropy = disorder (oversimplification)",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "apply", "analyze"],
      keyTerms: ["entropy", "熵", "Carnot", "卡诺", "second law", "第二定律"],
    },
    knownAITraps: ["AI may equate entropy with disorder without nuance"],
  },
  {
    id: "bi-cs-001",
    subject: "cs",
    en: {
      courseTitle: "Data Structures and Algorithms",
      title: "Binary Search Tree Operations",
      content: "BST insert, delete, search; balanced BSTs (AVL, Red-Black); time complexity",
    },
    zh: {
      courseTitle: "数据结构与算法",
      title: "二叉搜索树操作",
      content: "BST 的插入、删除、查找操作；平衡 BST（AVL 树、红黑树）；时间复杂度",
    },
    groundTruth: {
      correctFacts: [
        "BST search/insert/delete: O(h) where h = height",
        "Balanced BST: O(log n) guaranteed",
        "Unbalanced BST worst case: O(n) (degenerates to linked list)",
        "In-order traversal of BST yields sorted sequence",
      ],
      commonMisconceptions: [
        "BST operations are always O(log n)",
        "AVL and Red-Black trees have same balance criteria",
      ],
      expectedDifficulty: 3,
      bloomLevels: ["understand", "apply", "analyze"],
      keyTerms: ["BST", "二叉搜索树", "balanced", "平衡", "O(log n)", "AVL"],
    },
    knownAITraps: ["AI may say BST is always O(log n) without noting degenerate case"],
  },
  {
    id: "bi-econ-001",
    subject: "economics",
    en: {
      courseTitle: "Principles of Microeconomics",
      title: "Price Elasticity of Demand",
      content: "Measuring responsiveness of quantity demanded to price changes",
    },
    zh: {
      courseTitle: "微观经济学原理",
      title: "需求价格弹性",
      content: "衡量需求量对价格变化的敏感程度",
    },
    groundTruth: {
      correctFacts: [
        "PED = %ΔQd / %ΔP",
        "|PED| > 1 elastic, < 1 inelastic",
        "Revenue maximized at unit elastic point",
      ],
      commonMisconceptions: [
        "Steep curve = inelastic (depends on axis scale)",
        "Elasticity constant on linear demand curve (it varies)",
      ],
      expectedDifficulty: 2,
      bloomLevels: ["understand", "apply"],
      keyTerms: ["elasticity", "弹性", "elastic", "inelastic", "revenue"],
    },
    knownAITraps: ["AI may say elasticity is constant on linear demand curve"],
  },
];

// ─── Config ──────────────────────────────────────────────────

const args = process.argv.slice(2);
const modelId = args.includes("--model") ? args[args.indexOf("--model") + 1] : null;
const subjectFilter = args.includes("--subject") ? args[args.indexOf("--subject") + 1] as Subject : null;
const dryRun = args.includes("--dry-run");

interface LangResult {
  lang: "en" | "zh";
  kpId: string;
  subject: Subject;
  totalScore: number;
  questionCount: number;
  latencyMs: number;
  bloomDistribution: Record<string, number>;
  error?: string;
}

function evaluateQuick(
  questions: { type: string; stem: string; answer: string; explanation: string | null; difficulty: number; bloom_level: string; matched_kp_title: string }[],
  kp: BilingualKP,
): number {
  if (questions.length === 0) return 0;

  const scores: number[] = [];
  for (const q of questions) {
    const dims: DimensionScore[] = [];
    dims.push(scoreAnswerCorrectness(q.answer, kp.groundTruth.correctFacts, kp.knownAITraps));
    dims.push(scoreKpAlignment(q.stem, kp.groundTruth.keyTerms, kp.en.title));
    dims.push(scoreDifficultyCalibration(q.difficulty, kp.groundTruth.expectedDifficulty));
    dims.push(scoreBloomLevel(detectBloomLevel(q.stem), kp.groundTruth.bloomLevels));
    dims.push(scoreDiversity(questions));

    const hasWhy = q.explanation
      ? /because|since|the reason|incorrect|wrong|misconception|因为|原因|之所以|错误在于|误区|实际上/i.test(q.explanation)
      : false;
    const expLen = q.explanation?.length ?? 0;
    const expScore = hasWhy && expLen > 60 ? 5 : hasWhy && expLen > 30 ? 4 : expLen > 20 ? 3 : 2;
    dims.push({ dimension: "explanationQuality", score: q.explanation ? expScore : 1, maxScore: 5, weight: DIMENSIONS.explanationQuality.weight, details: "", automated: false });

    const stemLen = q.stem.length;
    const clarityScore = stemLen >= 20 && stemLen <= 300 ? 5 : stemLen >= 10 && stemLen <= 400 ? 4 : 3;
    dims.push({ dimension: "stemClarity", score: clarityScore, maxScore: 5, weight: DIMENSIONS.stemClarity.weight, details: "", automated: false });

    if (q.type === "multiple_choice") {
      dims.push({ dimension: "distractorQuality", score: 3, maxScore: 5, weight: DIMENSIONS.distractorQuality.weight, details: "heuristic", automated: false });
    } else {
      dims.push({ dimension: "distractorQuality", score: 0, maxScore: 5, weight: 0, details: "n/a", automated: false });
    }

    scores.push(computeWeightedTotal(dims));
  }

  return scores.reduce((a, b) => a + b, 0) / scores.length;
}

// ─── Mock generator for dry-run ─────────────────────────────

function mockGenerate(lang: "en" | "zh", kp: BilingualKP) {
  const data = lang === "en" ? kp.en : kp.zh;
  const q1Stem = lang === "en"
    ? `Which of the following best describes ${data.title}?`
    : `以下哪项最能描述${data.title}的核心概念？`;
  const q2Stem = lang === "en"
    ? `Calculate the result using the ${data.title} method.`
    : `运用${data.title}的方法，求解以下问题。`;

  return [
    {
      type: "multiple_choice",
      stem: q1Stem,
      options: [
        { label: "A", text: lang === "en" ? "Correct concept" : "正确概念" },
        { label: "B", text: lang === "en" ? "Common misconception" : "常见误解" },
        { label: "C", text: lang === "en" ? "Related but wrong" : "相关但错误" },
        { label: "D", text: lang === "en" ? "Unrelated fact" : "不相关的事实" },
      ],
      answer: "A",
      explanation: lang === "en"
        ? `The correct answer is A because ${kp.groundTruth.correctFacts[0]}. Students often incorrectly think ${kp.groundTruth.commonMisconceptions[0]}.`
        : `正确答案是A，因为${kp.groundTruth.correctFacts[0]}。学生常见的误区是${kp.groundTruth.commonMisconceptions[0]}。`,
      difficulty: kp.groundTruth.expectedDifficulty,
      bloom_level: kp.groundTruth.bloomLevels[0],
      matched_kp_title: data.title,
    },
    {
      type: "short_answer",
      stem: q2Stem,
      options: null,
      answer: kp.groundTruth.correctFacts[0],
      explanation: lang === "en"
        ? `This is because ${kp.groundTruth.correctFacts[1] ?? kp.groundTruth.correctFacts[0]}.`
        : `原因是${kp.groundTruth.correctFacts[1] ?? kp.groundTruth.correctFacts[0]}。`,
      difficulty: kp.groundTruth.expectedDifficulty,
      bloom_level: "apply",
      matched_kp_title: data.title,
    },
  ];
}

// ─── Main ────────────────────────────────────────────────────

async function main() {
  console.log("═══════════════════════════════════════════════════════════════");
  console.log("  CourseHub Bilingual Quality Comparison");
  console.log("  「Which language yields better content for each subject?」");
  console.log("═══════════════════════════════════════════════════════════════\n");

  // Resolve model
  let model: ModelConfig | undefined;
  if (dryRun) {
    model = MODELS[0]; // doesn't matter for dry-run
    console.log("  🧪 DRY RUN MODE (mock data)\n");
  } else {
    if (!modelId) {
      console.error("  ❌ --model <id> is required. Available:");
      for (const m of MODELS) {
        const hasKey = !!process.env[m.envKey];
        console.error(`    ${hasKey ? "✅" : "❌"} ${m.id}`);
      }
      process.exit(1);
    }
    model = MODELS.find(m => m.id === modelId && !!process.env[m.envKey]);
    if (!model) {
      console.error(`  ❌ Model "${modelId}" not found or API key missing`);
      process.exit(1);
    }
    console.log(`  Model: ${model.name} (${model.provider})\n`);
  }

  const kps = subjectFilter
    ? BILINGUAL_KPS.filter(k => k.subject === subjectFilter)
    : BILINGUAL_KPS;

  console.log(`  Testing ${kps.length} KPs × 2 languages = ${kps.length * 2} generation calls\n`);

  const results: LangResult[] = [];
  const generate = dryRun ? null : createModelGenerator(model!);

  for (const kp of kps) {
    for (const lang of ["en", "zh"] as const) {
      const data = lang === "en" ? kp.en : kp.zh;
      const startMs = Date.now();

      let questions: ReturnType<typeof mockGenerate>;
      try {
        if (dryRun) {
          questions = mockGenerate(lang, kp);
        } else {
          questions = await generate!(data.courseTitle, [{ title: data.title, content: data.content }]) as typeof questions;
        }
        const elapsed = Date.now() - startMs;
        const score = evaluateQuick(questions, kp);

        const bloomDist: Record<string, number> = {};
        for (const q of questions) {
          const bl = q.bloom_level ?? "unknown";
          bloomDist[bl] = (bloomDist[bl] ?? 0) + 1;
        }

        results.push({ lang, kpId: kp.id, subject: kp.subject, totalScore: score, questionCount: questions.length, latencyMs: elapsed, bloomDistribution: bloomDist });
        const icon = lang === "en" ? "🇬🇧" : "🇨🇳";
        console.log(`  ${icon} ${kp.id} [${lang.toUpperCase()}] ${data.title.padEnd(30)} → ${score.toFixed(1)}/100 (${questions.length} Qs, ${(elapsed / 1000).toFixed(1)}s)`);
      } catch (err) {
        const elapsed = Date.now() - startMs;
        results.push({ lang, kpId: kp.id, subject: kp.subject, totalScore: 0, questionCount: 0, latencyMs: elapsed, error: (err as Error).message.slice(0, 80) });
        console.log(`  ❌ ${kp.id} [${lang.toUpperCase()}] Error: ${(err as Error).message.slice(0, 60)}`);
      }
    }
  }

  // ─── Analysis ─────────────────────────────────────────────

  console.log("\n╔══════════════════════════════════════════════════════════════╗");
  console.log("║              BILINGUAL QUALITY ANALYSIS                     ║");
  console.log("╚══════════════════════════════════════════════════════════════╝\n");

  // Per-KP comparison
  console.log("  📊 Per-KP Language Comparison:");
  console.log("  " + "─".repeat(70));
  console.log("  " + "KP".padEnd(20) + "EN Score".padEnd(12) + "ZH Score".padEnd(12) + "Δ (EN-ZH)".padEnd(12) + "Winner");
  console.log("  " + "─".repeat(70));

  let enWins = 0, zhWins = 0, ties = 0;
  const subjectGaps: Record<string, { en: number[]; zh: number[] }> = {};

  for (const kp of kps) {
    const enResult = results.find(r => r.kpId === kp.id && r.lang === "en");
    const zhResult = results.find(r => r.kpId === kp.id && r.lang === "zh");
    const enScore = enResult?.totalScore ?? 0;
    const zhScore = zhResult?.totalScore ?? 0;
    const gap = enScore - zhScore;

    if (!subjectGaps[kp.subject]) subjectGaps[kp.subject] = { en: [], zh: [] };
    subjectGaps[kp.subject].en.push(enScore);
    subjectGaps[kp.subject].zh.push(zhScore);

    const winner = gap > 2 ? "🇬🇧 EN" : gap < -2 ? "🇨🇳 ZH" : "≈ TIE";
    if (gap > 2) enWins++;
    else if (gap < -2) zhWins++;
    else ties++;

    console.log(`  ${kp.id.padEnd(20)}${enScore.toFixed(1).padStart(5).padEnd(12)}${zhScore.toFixed(1).padStart(5).padEnd(12)}${(gap >= 0 ? "+" : "") + gap.toFixed(1).padStart(5).padEnd(12)}${winner}`);
  }

  // Subject-level summary
  console.log("\n  📚 Subject-Level Language Advantage:");
  console.log("  " + "─".repeat(60));

  const recommendations: Record<string, "en" | "zh" | "either"> = {};

  for (const [subject, scores] of Object.entries(subjectGaps)) {
    const avgEn = scores.en.reduce((a, b) => a + b, 0) / scores.en.length;
    const avgZh = scores.zh.reduce((a, b) => a + b, 0) / scores.zh.length;
    const gap = avgEn - avgZh;
    const label = SUBJECT_LABELS[subject as Subject] ?? subject;

    let recommendation: "en" | "zh" | "either";
    if (gap > 3) recommendation = "en";
    else if (gap < -3) recommendation = "zh";
    else recommendation = "either";
    recommendations[subject] = recommendation;

    const recStr = recommendation === "en" ? "→ Generate in EN, translate to ZH"
      : recommendation === "zh" ? "→ Generate in ZH directly"
      : "→ Either language OK";

    console.log(`  ${label.padEnd(30)} EN: ${avgEn.toFixed(1)} | ZH: ${avgZh.toFixed(1)} | Δ: ${(gap >= 0 ? "+" : "")}${gap.toFixed(1)}  ${recStr}`);
  }

  // Overall summary
  console.log("\n  🏆 Overall:");
  console.log(`  EN wins: ${enWins}  |  ZH wins: ${zhWins}  |  Ties: ${ties}`);
  console.log("\n  💡 Recommended generation strategy:");

  for (const [subject, rec] of Object.entries(recommendations)) {
    const label = SUBJECT_LABELS[subject as Subject] ?? subject;
    if (rec === "en") {
      console.log(`    ${label}: Generate in English → translate to user language`);
    } else if (rec === "zh") {
      console.log(`    ${label}: Generate directly in Chinese`);
    } else {
      console.log(`    ${label}: Language doesn't significantly affect quality`);
    }
  }

  // Save report
  const fs = await import("fs");
  const report = {
    timestamp: new Date().toISOString(),
    model: model?.id ?? "dry-run",
    results,
    subjectRecommendations: recommendations,
    summary: { enWins, zhWins, ties },
  };
  const path = `tests/ai-benchmark/bilingual-${model?.id ?? "dry-run"}-${new Date().toISOString().slice(0, 10)}.json`;
  fs.writeFileSync(path, JSON.stringify(report, null, 2));
  console.log(`\n  📄 Full report: ${path}`);
  console.log("═══════════════════════════════════════════════════════════════\n");
}

main().catch(err => {
  console.error("Bilingual comparison failed:", err);
  process.exit(1);
});
