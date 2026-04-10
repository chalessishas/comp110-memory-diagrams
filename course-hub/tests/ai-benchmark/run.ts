#!/usr/bin/env npx tsx
// ═══════════════════════════════════════════════════════════════
// CourseHub AI Benchmark Runner
// ═══════════════════════════════════════════════════════════════
//
// Usage: DASHSCOPE_API_KEY=xxx npx tsx tests/ai-benchmark/run.ts
//
// Runs generateQuestionsFromOutline against 30 KPs across 6 subjects,
// evaluates output on 8 dimensions, produces a JSON report + summary.
//
// Options:
//   --subject calculus    Run only one subject
//   --dry-run             Skip AI calls, test scoring pipeline with mock data
//   --output report.json  Custom output path

import { ALL_TEST_KPS, TEST_SUBJECTS, SUBJECT_LABELS, type Subject, type TestKnowledgePoint } from "./test-data";
import {
  DIMENSIONS,
  type DimensionKey,
  type QuestionEvaluation,
  type BenchmarkReport,
  scoreAnswerCorrectness,
  scoreKpAlignment,
  scoreDifficultyCalibration,
  scoreDiversity,
  scoreBloomLevel,
  detectBloomLevel,
  placeholderScore,
  computeWeightedTotal,
} from "./rubrics";

// ─── Config ──────────────────────────────────────────────────

const args = process.argv.slice(2);
const subjectFilter = args.includes("--subject") ? args[args.indexOf("--subject") + 1] as Subject : null;
const isDryRun = args.includes("--dry-run");
const outputIdx = args.indexOf("--output");
const outputPath = outputIdx >= 0 ? args[outputIdx + 1] : `tests/ai-benchmark/report-${new Date().toISOString().slice(0, 10)}.json`;

// ─── AI Pipeline Import ──────────────────────────────────────

async function callAI(courseTitle: string, kps: { title: string; content: string | null }[]) {
  if (isDryRun) return generateMockQuestions(kps);

  // Dynamic import to handle the module's env dependencies
  const { generateQuestionsFromOutline } = await import("../../src/lib/ai");
  return generateQuestionsFromOutline(courseTitle, kps);
}

interface GeneratedQuestion {
  type: string;
  stem: string;
  options: { label: string; text: string }[] | null;
  answer: string;
  explanation: string | null;
  difficulty: number;
  matched_kp_title: string;
}

function generateMockQuestions(kps: { title: string; content: string | null }[]): GeneratedQuestion[] {
  return kps.flatMap((kp) => [
    {
      type: "multiple_choice",
      stem: `What is the key concept in ${kp.title}?`,
      options: [
        { label: "A", text: "Correct answer related to the topic" },
        { label: "B", text: "Plausible distractor" },
        { label: "C", text: "Another distractor" },
        { label: "D", text: "Obviously wrong" },
      ],
      answer: "A",
      explanation: `The key concept in ${kp.title} is fundamental because...`,
      difficulty: 3,
      matched_kp_title: kp.title,
    },
    {
      type: "fill_blank",
      stem: `The formula for ${kp.title} involves _____.`,
      options: null,
      answer: "the correct term",
      explanation: null,
      difficulty: 2,
      matched_kp_title: kp.title,
    },
  ]);
}

// ─── Evaluate a single question ──────────────────────────────

function evaluateQuestion(
  q: GeneratedQuestion,
  kp: TestKnowledgePoint,
  questionIndex: number,
  allQsForKp: GeneratedQuestion[],
): QuestionEvaluation {
  const flags: string[] = [];
  const dimensions = [];

  // D1: Answer Correctness (automated)
  const d1 = scoreAnswerCorrectness(q.answer, kp.groundTruth.correctFacts, kp.knownAITraps);
  dimensions.push(d1);
  if (d1.score <= 2) flags.push(`CRITICAL: Answer may be wrong — ${d1.details}`);

  // D2: Distractor Quality (human review needed for MCQ)
  if (q.type === "multiple_choice" && q.options) {
    // Heuristic: check if any distractor mentions a known misconception keyword
    const distractors = q.options.filter(o => o.label !== q.answer);
    const miscKeywords = kp.groundTruth.commonMisconceptions
      .flatMap(m => m.toLowerCase().split(/\s+/).filter(w => w.length > 4));
    const distractorText = distractors.map(d => d.text.toLowerCase()).join(" ");
    const miscHits = miscKeywords.filter(kw => distractorText.includes(kw)).length;
    const miscRatio = miscKeywords.length > 0 ? miscHits / Math.min(miscKeywords.length, 5) : 0;

    dimensions.push({
      dimension: "distractorQuality",
      score: miscRatio >= 0.3 ? 4 : miscRatio >= 0.1 ? 3 : 2,
      maxScore: 5 as const,
      weight: DIMENSIONS.distractorQuality.weight,
      details: `${miscHits} misconception keywords found in distractors (heuristic — needs human review)`,
      automated: false,
    });
  } else {
    dimensions.push(placeholderScore("distractorQuality"));
  }

  // D3: KP Alignment (automated)
  dimensions.push(scoreKpAlignment(q.stem, kp.groundTruth.keyTerms, kp.title));

  // D4: Difficulty Calibration (automated)
  dimensions.push(scoreDifficultyCalibration(q.difficulty, kp.groundTruth.expectedDifficulty));

  // D5: Bloom's Level (heuristic)
  const detected = detectBloomLevel(q.stem);
  dimensions.push(scoreBloomLevel(detected, kp.groundTruth.bloomLevels));

  // D6: Stem Clarity (human review)
  // Heuristic: check length (too short = vague, too long = confusing)
  const stemLen = q.stem.length;
  const clarityScore = stemLen >= 20 && stemLen <= 300 ? 4 : stemLen < 20 ? 2 : 3;
  dimensions.push({
    dimension: "stemClarity",
    score: clarityScore,
    maxScore: 5 as const,
    weight: DIMENSIONS.stemClarity.weight,
    details: `Stem length: ${stemLen} chars (heuristic — needs human review)`,
    automated: false,
  });

  // D7: Explanation Quality (human review)
  if (q.explanation) {
    const expLen = q.explanation.length;
    const hasWhy = /because|since|this is because|the reason/i.test(q.explanation);
    const expScore = hasWhy && expLen > 30 ? 4 : expLen > 20 ? 3 : 2;
    dimensions.push({
      dimension: "explanationQuality",
      score: expScore,
      maxScore: 5 as const,
      weight: DIMENSIONS.explanationQuality.weight,
      details: `Length: ${expLen}, Has 'why': ${hasWhy} (heuristic — needs human review)`,
      automated: false,
    });
  } else {
    dimensions.push({
      dimension: "explanationQuality",
      score: 1,
      maxScore: 5 as const,
      weight: DIMENSIONS.explanationQuality.weight,
      details: "No explanation provided",
      automated: true,
    });
    flags.push("Missing explanation");
  }

  // D8: Diversity (across all questions for this KP)
  dimensions.push(scoreDiversity(allQsForKp));

  const totalScore = computeWeightedTotal(dimensions);

  return {
    testKpId: kp.id,
    questionIndex,
    questionType: q.type,
    stem: q.stem,
    dimensions,
    totalScore,
    flags,
  };
}

// ─── Main Runner ─────────────────────────────────────────────

async function runBenchmark() {
  console.log("═══════════════════════════════════════════════════");
  console.log("  CourseHub AI Teaching Content Benchmark");
  console.log(`  ${isDryRun ? "DRY RUN (mock data)" : "LIVE (calling AI)"}`);
  console.log("═══════════════════════════════════════════════════\n");

  const testKPs = subjectFilter
    ? (TEST_SUBJECTS[subjectFilter] ?? [])
    : ALL_TEST_KPS;

  if (testKPs.length === 0) {
    console.error(`No KPs found for subject: ${subjectFilter}`);
    process.exit(1);
  }

  console.log(`Testing ${testKPs.length} KPs across ${subjectFilter ?? "all"} subjects\n`);

  const allEvals: QuestionEvaluation[] = [];
  const subjectStats: Record<string, { scores: number[]; count: number }> = {};

  // Group KPs by course for batching (API generates 2-3 per KP)
  const byCourse = new Map<string, TestKnowledgePoint[]>();
  for (const kp of testKPs) {
    const list = byCourse.get(kp.courseTitle) ?? [];
    list.push(kp);
    byCourse.set(kp.courseTitle, list);
  }

  for (const [courseTitle, kps] of byCourse) {
    const subjectName = SUBJECT_LABELS[kps[0].subject as Subject] ?? kps[0].subject;
    console.log(`\n📚 ${subjectName} — ${courseTitle}`);
    console.log("─".repeat(50));

    // Process in batches of 5 (matching MAX_KPS_PER_CALL)
    for (let i = 0; i < kps.length; i += 5) {
      const batch = kps.slice(i, i + 5);
      const kpData = batch.map(kp => ({ title: kp.title, content: kp.content }));

      let questions: GeneratedQuestion[];
      try {
        console.log(`  Generating for ${batch.map(k => k.id).join(", ")}...`);
        questions = await callAI(courseTitle, kpData) as GeneratedQuestion[];
        console.log(`  → ${questions.length} questions generated`);
      } catch (err) {
        console.error(`  ❌ Generation failed: ${err instanceof Error ? err.message : err}`);
        continue;
      }

      // Evaluate each question
      for (const kp of batch) {
        const kpQuestions = questions.filter(
          q => q.matched_kp_title.toLowerCase() === kp.title.toLowerCase()
        );

        if (kpQuestions.length === 0) {
          console.log(`  ⚠️  No questions matched KP: ${kp.title}`);
          continue;
        }

        for (let qi = 0; qi < kpQuestions.length; qi++) {
          const evaluation = evaluateQuestion(kpQuestions[qi], kp, qi, kpQuestions);
          allEvals.push(evaluation);

          // Track by subject
          const sub = kp.subject;
          if (!subjectStats[sub]) subjectStats[sub] = { scores: [], count: 0 };
          subjectStats[sub].scores.push(evaluation.totalScore);
          subjectStats[sub].count++;

          // Log critical flags
          if (evaluation.flags.length > 0) {
            console.log(`  🚩 ${kp.id} Q${qi}: ${evaluation.flags[0]}`);
          }
        }

        const avgScore = kpQuestions.reduce((sum, _, qi) => {
          const ev = allEvals.find(e => e.testKpId === kp.id && e.questionIndex === qi);
          return sum + (ev?.totalScore ?? 0);
        }, 0) / kpQuestions.length;

        const emoji = avgScore >= 80 ? "✅" : avgScore >= 60 ? "⚠️" : "❌";
        console.log(`  ${emoji} ${kp.id}: ${avgScore.toFixed(1)}/100 (${kpQuestions.length} questions)`);
      }
    }
  }

  // ─── Build Report ────────────────────────────────────────

  const overallScore = allEvals.length > 0
    ? allEvals.reduce((s, e) => s + e.totalScore, 0) / allEvals.length
    : 0;

  const bySubject: Record<string, { avgScore: number; questionCount: number }> = {};
  for (const [sub, stats] of Object.entries(subjectStats)) {
    bySubject[sub] = {
      avgScore: stats.scores.reduce((a, b) => a + b, 0) / stats.scores.length,
      questionCount: stats.count,
    };
  }

  const byDimension: Record<string, { avgScore: number; distribution: number[] }> = {};
  for (const dimKey of Object.keys(DIMENSIONS) as DimensionKey[]) {
    const scores = allEvals
      .flatMap(e => e.dimensions)
      .filter(d => d.dimension === dimKey && d.score > 0)
      .map(d => d.score);

    const dist = [0, 0, 0, 0, 0]; // count of 1s, 2s, 3s, 4s, 5s
    for (const s of scores) dist[s - 1]++;

    byDimension[dimKey] = {
      avgScore: scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 0,
      distribution: dist,
    };
  }

  const criticalFlags = allEvals.flatMap(e => e.flags.filter(f => f.startsWith("CRITICAL")));

  const report: BenchmarkReport = {
    timestamp: new Date().toISOString(),
    totalKPs: testKPs.length,
    totalQuestions: allEvals.length,
    overallScore,
    bySubject,
    byDimension,
    criticalFlags,
    questions: allEvals,
  };

  // ─── Output ──────────────────────────────────────────────

  const fs = await import("fs");
  fs.writeFileSync(outputPath, JSON.stringify(report, null, 2));
  console.log(`\n📊 Report saved to ${outputPath}`);

  // Summary
  console.log("\n═══════════════════════════════════════════════════");
  console.log("  BENCHMARK SUMMARY");
  console.log("═══════════════════════════════════════════════════");
  console.log(`  Overall Score:  ${overallScore.toFixed(1)}/100`);
  console.log(`  Questions:      ${allEvals.length}`);
  console.log(`  Critical Flags: ${criticalFlags.length}`);
  console.log("");
  console.log("  By Subject:");
  for (const [sub, stats] of Object.entries(bySubject)) {
    const label = SUBJECT_LABELS[sub as Subject] ?? sub;
    const bar = "█".repeat(Math.round(stats.avgScore / 5));
    console.log(`    ${label.padEnd(35)} ${stats.avgScore.toFixed(1).padStart(5)} ${bar}`);
  }
  console.log("");
  console.log("  By Dimension:");
  for (const [dim, stats] of Object.entries(byDimension)) {
    const name = DIMENSIONS[dim as DimensionKey]?.nameZh ?? dim;
    const bar = "█".repeat(Math.round(stats.avgScore));
    console.log(`    ${name.padEnd(20)} ${stats.avgScore.toFixed(2).padStart(5)}/5 ${bar}`);
  }

  if (criticalFlags.length > 0) {
    console.log("\n  🚨 Critical Issues:");
    for (const flag of criticalFlags.slice(0, 10)) {
      console.log(`    - ${flag}`);
    }
  }

  console.log("\n═══════════════════════════════════════════════════\n");

  // Exit with error code if score is below threshold
  if (overallScore < 60) {
    console.log("❌ FAIL: Overall score below 60/100 threshold");
    process.exit(1);
  }
}

runBenchmark().catch((err) => {
  console.error("Benchmark failed:", err);
  process.exit(1);
});
