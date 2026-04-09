#!/usr/bin/env npx tsx
// ═══════════════════════════════════════════════════════════════
// Multi-Model Comparison Runner
// ═══════════════════════════════════════════════════════════════
//
// Runs the same benchmark across all available models and produces
// a side-by-side comparison report.
//
// Usage:
//   DASHSCOPE_API_KEY=xxx DEEPSEEK_API_KEY=yyy OPENAI_API_KEY=zzz \
//   GEMINI_API_KEY=aaa ANTHROPIC_API_KEY=bbb \
//   npx tsx tests/ai-benchmark/compare-models.ts
//
// Options:
//   --subject calculus     Test one subject only (faster, cheaper)
//   --models qwen3.5-plus,deepseek-chat   Test specific models only
//   --kps-per-subject 2   Limit KPs per subject (default: all 5)

import { TEST_SUBJECTS, SUBJECT_LABELS, ALL_TEST_KPS, type Subject, type TestKnowledgePoint } from "./test-data";
import { getAvailableModels, createModelGenerator, MODELS, type ModelConfig } from "./models";
import {
  DIMENSIONS,
  type DimensionKey,
  scoreAnswerCorrectness,
  scoreKpAlignment,
  scoreDifficultyCalibration,
  scoreDiversity,
  scoreBloomLevel,
  detectBloomLevel,
  computeWeightedTotal,
  type DimensionScore,
} from "./rubrics";

// ─── Config ──────────────────────────────────────────────────

const args = process.argv.slice(2);
const subjectFilter = args.includes("--subject") ? args[args.indexOf("--subject") + 1] as Subject : null;
const modelsFilter = args.includes("--models") ? args[args.indexOf("--models") + 1].split(",") : null;
const kpsPerSubject = args.includes("--kps-per-subject") ? parseInt(args[args.indexOf("--kps-per-subject") + 1]) : 999;

interface GeneratedQ {
  type: string;
  stem: string;
  options: { label: string; text: string }[] | null;
  answer: string;
  explanation: string | null;
  difficulty: number;
  bloom_level: string;
  matched_kp_title: string;
}

interface ModelResult {
  modelId: string;
  modelName: string;
  provider: string;
  costPerMInput: number;
  costPerMOutput: number;
  totalQuestions: number;
  avgScore: number;
  byDimension: Record<string, number>;
  bySubject: Record<string, number>;
  avgLatencyMs: number;
  errors: number;
  jsonParseFailures: number;
  bloomDistribution: Record<string, number>;
  sampleQuestions: { kpId: string; stem: string; answer: string; score: number }[];
}

function evaluateQuestionQuick(
  q: GeneratedQ,
  kp: TestKnowledgePoint,
  allQsForKp: GeneratedQ[],
): { totalScore: number; dimensions: Record<string, number> } {
  const dims: DimensionScore[] = [];

  dims.push(scoreAnswerCorrectness(q.answer, kp.groundTruth.correctFacts, kp.knownAITraps));
  dims.push(scoreKpAlignment(q.stem, kp.groundTruth.keyTerms, kp.title));
  dims.push(scoreDifficultyCalibration(q.difficulty, kp.groundTruth.expectedDifficulty));

  const detected = detectBloomLevel(q.stem);
  dims.push(scoreBloomLevel(detected, kp.groundTruth.bloomLevels));
  dims.push(scoreDiversity(allQsForKp));

  // Explanation quality heuristic
  if (q.explanation) {
    const hasWhy = /because|since|this is because|the reason|incorrect because|wrong because|misconception/i.test(q.explanation);
    const expLen = q.explanation.length;
    const expScore = hasWhy && expLen > 60 ? 5 : hasWhy && expLen > 30 ? 4 : expLen > 20 ? 3 : 2;
    dims.push({ dimension: "explanationQuality", score: expScore, maxScore: 5, weight: DIMENSIONS.explanationQuality.weight, details: "", automated: false });
  } else {
    dims.push({ dimension: "explanationQuality", score: 1, maxScore: 5, weight: DIMENSIONS.explanationQuality.weight, details: "missing", automated: true });
  }

  // Stem clarity heuristic
  const stemLen = q.stem.length;
  const clarityScore = stemLen >= 30 && stemLen <= 250 ? 5 : stemLen >= 20 && stemLen <= 300 ? 4 : 3;
  dims.push({ dimension: "stemClarity", score: clarityScore, maxScore: 5, weight: DIMENSIONS.stemClarity.weight, details: "", automated: false });

  // Distractor quality (MCQ only)
  if (q.type === "multiple_choice" && q.options && q.options.length >= 4) {
    const distractors = q.options.filter(o => o.label !== q.answer);
    const miscKeywords = kp.groundTruth.commonMisconceptions.flatMap(m => m.toLowerCase().split(/\s+/).filter(w => w.length > 4));
    const distractorText = distractors.map(d => d.text.toLowerCase()).join(" ");
    const miscHits = miscKeywords.filter(kw => distractorText.includes(kw)).length;
    const miscRatio = miscKeywords.length > 0 ? miscHits / Math.min(miscKeywords.length, 5) : 0;
    dims.push({ dimension: "distractorQuality", score: miscRatio >= 0.3 ? 4 : miscRatio >= 0.1 ? 3 : 2, maxScore: 5, weight: DIMENSIONS.distractorQuality.weight, details: "", automated: false });
  } else {
    dims.push({ dimension: "distractorQuality", score: 0, maxScore: 5, weight: 0, details: "n/a", automated: false });
  }

  const dimensionMap: Record<string, number> = {};
  for (const d of dims) {
    if (d.score > 0) dimensionMap[d.dimension] = d.score;
  }

  return { totalScore: computeWeightedTotal(dims), dimensions: dimensionMap };
}

// ─── Main ────────────────────────────────────────────────────

async function main() {
  console.log("═══════════════════════════════════════════════════════════════");
  console.log("  CourseHub Multi-Model Comparison Benchmark");
  console.log("═══════════════════════════════════════════════════════════════\n");

  // Check available models
  const available = getAvailableModels();
  const selected = modelsFilter
    ? available.filter(m => modelsFilter.includes(m.id))
    : available;

  console.log("  Available models:");
  for (const m of MODELS) {
    const hasKey = !!process.env[m.envKey];
    const isSelected = selected.some(s => s.id === m.id);
    const icon = isSelected ? "✅" : hasKey ? "⬜" : "❌";
    const tierTag = `[${m.tier}]`;
    console.log(`    ${icon} ${m.name.padEnd(30)} ${m.provider.padEnd(24)} $${m.pricePerMInput}/$${m.pricePerMOutput}/M  ${tierTag.padEnd(14)} ${hasKey ? "" : `(missing ${m.envKey})`}`);
  }

  if (selected.length === 0) {
    console.error("\n  ❌ No models available. Set at least one API key:");
    console.error("     DASHSCOPE_API_KEY, DEEPSEEK_API_KEY, OPENAI_API_KEY, GEMINI_API_KEY, or ANTHROPIC_API_KEY");
    process.exit(1);
  }

  // Prepare test data
  let testKPs: TestKnowledgePoint[];
  if (subjectFilter) {
    testKPs = (TEST_SUBJECTS[subjectFilter] ?? []).slice(0, kpsPerSubject);
  } else {
    testKPs = [];
    for (const subject of Object.keys(TEST_SUBJECTS) as Subject[]) {
      testKPs.push(...TEST_SUBJECTS[subject].slice(0, kpsPerSubject));
    }
  }

  console.log(`\n  Testing ${testKPs.length} KPs across ${selected.length} models\n`);

  const results: ModelResult[] = [];

  for (const model of selected) {
    console.log(`\n${"═".repeat(60)}`);
    console.log(`  🤖 ${model.name} (${model.provider})`);
    console.log(`${"═".repeat(60)}`);

    const generate = createModelGenerator(model);
    const result: ModelResult = {
      modelId: model.id,
      modelName: model.name,
      provider: model.provider,
      costPerMInput: model.pricePerMInput,
      costPerMOutput: model.pricePerMOutput,
      totalQuestions: 0,
      avgScore: 0,
      byDimension: {},
      bySubject: {},
      avgLatencyMs: 0,
      errors: 0,
      jsonParseFailures: 0,
      bloomDistribution: {},
      sampleQuestions: [],
    };

    const allScores: number[] = [];
    const dimScores: Record<string, number[]> = {};
    const subjectScores: Record<string, number[]> = {};
    const latencies: number[] = [];

    // Group by course for batching
    const byCourse = new Map<string, TestKnowledgePoint[]>();
    for (const kp of testKPs) {
      const list = byCourse.get(kp.courseTitle) ?? [];
      list.push(kp);
      byCourse.set(kp.courseTitle, list);
    }

    for (const [courseTitle, kps] of byCourse) {
      // Process in batches of 5
      for (let i = 0; i < kps.length; i += 5) {
        const batch = kps.slice(i, i + 5);
        const kpData = batch.map(kp => ({ title: kp.title, content: kp.content }));

        const startMs = Date.now();
        let questions: GeneratedQ[];

        try {
          console.log(`  Generating: ${batch.map(k => k.id).join(", ")}...`);
          questions = await generate(courseTitle, kpData) as GeneratedQ[];
          const elapsed = Date.now() - startMs;
          latencies.push(elapsed);
          console.log(`  → ${questions.length} questions in ${(elapsed / 1000).toFixed(1)}s`);
        } catch (err) {
          const elapsed = Date.now() - startMs;
          latencies.push(elapsed);
          const msg = err instanceof Error ? err.message : String(err);
          if (msg.includes("JSON") || msg.includes("parse")) {
            result.jsonParseFailures++;
            console.log(`  ⚠️  JSON parse failure (${(elapsed / 1000).toFixed(1)}s): ${msg.slice(0, 80)}`);
          } else {
            result.errors++;
            console.log(`  ❌ Error (${(elapsed / 1000).toFixed(1)}s): ${msg.slice(0, 80)}`);
          }
          continue;
        }

        // Evaluate
        for (const kp of batch) {
          const kpQs = questions.filter(q => q.matched_kp_title.toLowerCase() === kp.title.toLowerCase());
          if (kpQs.length === 0) continue;

          for (const q of kpQs) {
            const { totalScore, dimensions } = evaluateQuestionQuick(q, kp, kpQs);
            allScores.push(totalScore);
            result.totalQuestions++;

            // Track Bloom distribution
            const bl = q.bloom_level ?? "unknown";
            result.bloomDistribution[bl] = (result.bloomDistribution[bl] ?? 0) + 1;

            // Track dimension scores
            for (const [dim, score] of Object.entries(dimensions)) {
              if (!dimScores[dim]) dimScores[dim] = [];
              dimScores[dim].push(score);
            }

            // Track by subject
            const sub = kp.subject;
            if (!subjectScores[sub]) subjectScores[sub] = [];
            subjectScores[sub].push(totalScore);

            // Keep sample questions (best and worst)
            result.sampleQuestions.push({
              kpId: kp.id,
              stem: q.stem.slice(0, 100),
              answer: q.answer.slice(0, 50),
              score: totalScore,
            });
          }
        }
      }
    }

    // Compute averages
    result.avgScore = allScores.length > 0 ? allScores.reduce((a, b) => a + b, 0) / allScores.length : 0;
    result.avgLatencyMs = latencies.length > 0 ? latencies.reduce((a, b) => a + b, 0) / latencies.length : 0;

    for (const [dim, scores] of Object.entries(dimScores)) {
      result.byDimension[dim] = scores.reduce((a, b) => a + b, 0) / scores.length;
    }
    for (const [sub, scores] of Object.entries(subjectScores)) {
      result.bySubject[sub] = scores.reduce((a, b) => a + b, 0) / scores.length;
    }

    // Sort samples by score
    result.sampleQuestions.sort((a, b) => a.score - b.score);

    results.push(result);

    console.log(`\n  Score: ${result.avgScore.toFixed(1)}/100 | Qs: ${result.totalQuestions} | Latency: ${(result.avgLatencyMs / 1000).toFixed(1)}s | Errors: ${result.errors} | JSON failures: ${result.jsonParseFailures}`);
  }

  // ─── Comparison Report ───────────────────────────────────

  console.log("\n\n");
  console.log("╔══════════════════════════════════════════════════════════════╗");
  console.log("║              MULTI-MODEL COMPARISON REPORT                  ║");
  console.log("╚══════════════════════════════════════════════════════════════╝\n");

  // Overall ranking
  const ranked = [...results].sort((a, b) => b.avgScore - a.avgScore);

  console.log("  📊 Overall Ranking:");
  console.log("  ─────────────────────────────────────────────────────────────");
  console.log("  " + "Rank".padEnd(6) + "Model".padEnd(25) + "Score".padEnd(10) + "Latency".padEnd(12) + "Cost/M".padEnd(12) + "Questions".padEnd(10) + "Errors");
  console.log("  " + "─".repeat(80));

  for (let i = 0; i < ranked.length; i++) {
    const r = ranked[i];
    const medal = i === 0 ? "🥇" : i === 1 ? "🥈" : i === 2 ? "🥉" : "  ";
    const cost = `$${r.costPerMInput}/$${r.costPerMOutput}`;
    console.log(
      `  ${medal} ${String(i + 1).padEnd(4)}${r.modelName.padEnd(25)}${r.avgScore.toFixed(1).padStart(5).padEnd(10)}${(r.avgLatencyMs / 1000).toFixed(1).padStart(5)}s${" ".repeat(6)}${cost.padEnd(12)}${String(r.totalQuestions).padEnd(10)}${r.errors + r.jsonParseFailures}`
    );
  }

  // Dimension breakdown
  const dimKeys = Object.keys(DIMENSIONS) as DimensionKey[];
  console.log("\n  📐 By Dimension (avg score /5):");
  console.log("  ─────────────────────────────────────────────────────────────");
  const dimHeader = "  " + "Dimension".padEnd(22) + ranked.map(r => r.modelName.slice(0, 12).padEnd(14)).join("");
  console.log(dimHeader);
  console.log("  " + "─".repeat(22 + ranked.length * 14));

  for (const dk of dimKeys) {
    const name = DIMENSIONS[dk].nameZh;
    const scores = ranked.map(r => {
      const s = r.byDimension[dk];
      return s !== undefined ? s.toFixed(2).padStart(5).padEnd(14) : "  n/a".padEnd(14);
    }).join("");
    console.log(`  ${name.padEnd(22)}${scores}`);
  }

  // Subject breakdown
  console.log("\n  📚 By Subject:");
  console.log("  ─────────────────────────────────────────────────────────────");
  const subHeader = "  " + "Subject".padEnd(22) + ranked.map(r => r.modelName.slice(0, 12).padEnd(14)).join("");
  console.log(subHeader);
  console.log("  " + "─".repeat(22 + ranked.length * 14));

  for (const sub of Object.keys(TEST_SUBJECTS) as Subject[]) {
    const label = SUBJECT_LABELS[sub].slice(0, 20);
    const scores = ranked.map(r => {
      const s = r.bySubject[sub];
      return s !== undefined ? s.toFixed(1).padStart(5).padEnd(14) : "  n/a".padEnd(14);
    }).join("");
    console.log(`  ${label.padEnd(22)}${scores}`);
  }

  // Bloom distribution
  console.log("\n  🧠 Bloom Level Distribution:");
  console.log("  ─────────────────────────────────────────────────────────────");
  const bloomLevels = ["remember", "understand", "apply", "analyze", "evaluate", "create"];
  const bloomHeader = "  " + "Level".padEnd(14) + ranked.map(r => r.modelName.slice(0, 12).padEnd(14)).join("");
  console.log(bloomHeader);
  console.log("  " + "─".repeat(14 + ranked.length * 14));

  for (const bl of bloomLevels) {
    const counts = ranked.map(r => {
      const c = r.bloomDistribution[bl] ?? 0;
      const total = r.totalQuestions || 1;
      return `${c} (${Math.round(c / total * 100)}%)`.padEnd(14);
    }).join("");
    console.log(`  ${bl.padEnd(14)}${counts}`);
  }

  // Cost-quality tradeoff
  console.log("\n  💰 Cost-Quality Tradeoff:");
  console.log("  ─────────────────────────────────────────────────────────────");
  for (const r of ranked) {
    const qualityPerDollar = r.costPerMInput > 0 ? (r.avgScore / r.costPerMInput).toFixed(1) : "∞";
    const bar = "█".repeat(Math.round(r.avgScore / 5));
    console.log(`  ${r.modelName.padEnd(25)} ${r.avgScore.toFixed(1).padStart(5)}/100  $${r.costPerMInput}/M  quality/$ = ${qualityPerDollar.padStart(6)}  ${bar}`);
  }

  // Save report
  const fs = await import("fs");
  const reportPath = `tests/ai-benchmark/comparison-${new Date().toISOString().slice(0, 10)}.json`;
  fs.writeFileSync(reportPath, JSON.stringify({ timestamp: new Date().toISOString(), results: ranked }, null, 2));
  console.log(`\n  📄 Full report: ${reportPath}`);
  console.log("═══════════════════════════════════════════════════════════════\n");
}

main().catch(err => {
  console.error("Comparison failed:", err);
  process.exit(1);
});
