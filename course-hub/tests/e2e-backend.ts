/**
 * E2E Backend Test — Tests all API routes with real Supabase auth
 *
 * Scenario 1: Create course → Parse full Calculus II outline
 * Scenario 2: Set midterm exam → Generate exam prep questions
 *
 * Usage: SUPABASE_URL=... SUPABASE_KEY=... npx tsx tests/e2e-backend.ts
 */

import { createClient } from "@supabase/supabase-js";

// ─── Config ────────────────────────────────────────
const BASE = process.env.BASE_URL ?? "http://localhost:3098";
const SUPABASE_URL = process.env.NEXT_PUBLIC_SUPABASE_URL ?? "https://zubvbcexqaiauyptsyby.supabase.co";
const SUPABASE_SERVICE_KEY = process.env.SUPABASE_SERVICE_ROLE_KEY ?? "";
const SUPABASE_ANON_KEY = process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ?? "";

const TEST_EMAIL = "e2e-test@coursehub.local";
const TEST_PASSWORD = "test-password-123!";

const supabaseAdmin = createClient(SUPABASE_URL, SUPABASE_SERVICE_KEY, {
  auth: { autoRefreshToken: false, persistSession: false },
});

// ─── State ─────────────────────────────────────────
let fullSession: unknown = null;
let courseId = "";
let questionIds: string[] = [];
let knowledgePointIds: string[] = [];

// ─── Helpers ───────────────────────────────────────
function cookie() {
  // Supabase SSR expects base64url-encoded session with "base64-" prefix
  const ref = SUPABASE_URL.match(/\/\/(.*?)\.supabase/)?.[1] ?? "local";
  const key = `sb-${ref}-auth-token`;
  const payload = JSON.stringify(fullSession);
  const b64url = "base64-" + Buffer.from(payload).toString("base64url");

  // Chunk at 3180 chars (Supabase default)
  const CHUNK = 3180;
  const chunks: string[] = [];
  for (let i = 0; i < b64url.length; i += CHUNK) chunks.push(b64url.slice(i, i + CHUNK));

  if (chunks.length === 1) return `${key}=${chunks[0]}`;
  return chunks.map((c, i) => `${key}.${i}=${c}`).join("; ");
}

async function api(method: string, path: string, body?: unknown, timeoutMs = 300_000) {
  const url = `${BASE}${path}`;
  try {
    const res = await fetch(url, {
      method,
      headers: {
        "Content-Type": "application/json",
        Cookie: cookie(),
      },
      body: body ? JSON.stringify(body) : undefined,
      signal: AbortSignal.timeout(timeoutMs),
    });
    const text = await res.text();
    let data: unknown;
    try { data = JSON.parse(text); } catch { data = text; }
    return { status: res.status, data, ok: res.ok };
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    return { status: 0, data: { error: `fetch failed: ${msg}` }, ok: false };
  }
}

function log(label: string, result: { status: number; data: unknown; ok: boolean }) {
  const icon = result.ok ? "✓" : "✗";
  const statusColor = result.ok ? "\x1b[32m" : "\x1b[31m";
  console.log(`${statusColor}${icon}\x1b[0m [${result.status}] ${label}`);
  if (!result.ok) {
    console.log("  Error:", JSON.stringify(result.data).slice(0, 200));
  }
}

function logDetail(label: string, detail: string) {
  console.log(`  → ${label}: ${detail}`);
}

// ─── Auth Setup ────────────────────────────────────
async function setupAuth() {
  console.log("\n═══ Auth Setup ═══");

  // Try to create test user (ignore if exists)
  const { data: existingUsers } = await supabaseAdmin.auth.admin.listUsers();
  const existing = existingUsers?.users?.find(u => u.email === TEST_EMAIL);

  if (existing) {
    console.log(`  Using existing test user: ${TEST_EMAIL}`);
  } else {
    const { error } = await supabaseAdmin.auth.admin.createUser({
      email: TEST_EMAIL,
      password: TEST_PASSWORD,
      email_confirm: true,
    });
    if (error) throw new Error(`Failed to create test user: ${error.message}`);
    console.log(`  Created test user: ${TEST_EMAIL}`);
  }

  // Sign in to get access token
  const anonClient = createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
  const { data: session, error: signInError } = await anonClient.auth.signInWithPassword({
    email: TEST_EMAIL,
    password: TEST_PASSWORD,
  });

  if (signInError || !session.session) {
    throw new Error(`Failed to sign in: ${signInError?.message}`);
  }

  fullSession = session.session;
  console.log(`  Got access token: ${session.session.access_token.slice(0, 20)}...`);
}

// ─── Scenario 1: Full Outline ──────────────────────
async function scenario1_fullOutline() {
  console.log("\n═══ Scenario 1: Create Course + Parse Full Calculus II Outline ═══\n");

  // Step 1: Create course
  console.log("--- Step 1: Create Course ---");
  const createRes = await api("POST", "/api/courses", {
    title: "MATH 232 — Calculus II",
    description: "Integral calculus, sequences, series, parametric/polar curves",
    professor: "Dr. Joe",
    semester: "Spring 2026",
  });
  log("POST /api/courses", createRes);
  if (!createRes.ok) return;
  courseId = (createRes.data as any).id;
  logDetail("Course ID", courseId);

  // Step 2: Parse syllabus text → outline
  console.log("\n--- Step 2: Parse Syllabus → Outline ---");
  const syllabusText = `MATH 232 — Calculus II, Spring 2026, Dr. Joe

Schedule:
1/7 Introduction
1/9 2.1 Area Between Curves
1/12 2.2 Volume by Slicing
1/14 2.5 Physical Applications
1/16 3.1 Integration by Parts
1/19 NO CLASS
1/21 3.1 Integration by Parts, 3.2 Trig Integrals
1/23 3.2 Trigonometric Integrals
1/26 3.3 Trigonometric Substitution
1/28 3.3 Trig Sub, 3.4 Partial Fractions
1/30 3.4 Partial Fractions
2/2 3.5 Other Strategies of Integration
2/4 3.6 Numerical Integration
2/6 Test 1 (Sections 1.4-1.7, 2.1, 2.2, 2.5, 3.1 – 3.6)
2/9 NO CLASS
2/11 3.7 Improper Integrals
2/13 3.7 Improper Integrals
2/16 5.1 Sequences
2/18 5.2 Infinite Series
2/20 5.2 Infinite Series
2/23 5.3 Divergence and Integral Tests
2/25 5.3 Div and Int Tests
2/27 5.4 Comparison Tests
3/2 5.4 Comparison Tests
3/4 5.5 Alternating Series
3/6 5.5 Alternating Series
3/9 Convergence Test Strategies
3/11 Test 2 (Sections 3.7, 5.1 – 5.5)
3/13 5.6 Ratio and Root Tests
3/16 NO CLASS (Spring Break)
3/18 NO CLASS (Spring Break)
3/20 NO CLASS (Spring Break)
3/23 5.6 Ratio and Root Tests
3/25 6.1 Power Series and Functions
3/27 6.1 Power Series and Functions
3/30 6.2 Properties of Power Series
4/1 6.3 Taylor and Maclaurin Series
4/3 NO CLASS
4/6 6.3 Taylor and Maclaurin Series
4/8 6.4 Working with Taylor Series
4/10 Test 3 (Sections 5.6, 6.1 – 6.4)
4/13 4.1 Basics of Differential Equations
4/15 4.3 Separable Differential Equations
4/17 7.1 Parametric Equations
4/20 7.2 Calculus of Parametric Curves
4/22 7.3 Polar Coordinates
4/24 Review and Catch-up
4/27 Review and Catch-up`;

  const parseRes = await api("POST", "/api/parse", {
    parseType: "syllabus",
    rawText: syllabusText,
    language: "en",
  });
  log("POST /api/parse (syllabus)", parseRes);
  if (!parseRes.ok) return;

  const parsed = parseRes.data as any;
  logDetail("Parsed title", parsed.data?.title ?? "N/A");
  logDetail("Confidence", parsed.data?.confidence ?? "N/A");
  logDetail("Top-level nodes", String(parsed.data?.nodes?.length ?? 0));

  // Count all knowledge points recursively
  function countKPs(nodes: any[]): number {
    let count = 0;
    for (const n of nodes ?? []) {
      if (n.type === "knowledge_point") count++;
      count += countKPs(n.children ?? []);
    }
    return count;
  }
  logDetail("Knowledge points", String(countKPs(parsed.data?.nodes ?? [])));

  // Step 3: Save outline to course
  console.log("\n--- Step 3: Save Outline to Course ---");
  if (parsed.data?.nodes) {
    const outlineRes = await api("PUT", `/api/courses/${courseId}/outline`, {
      nodes: parsed.data.nodes,
      version: new Date().toISOString(),
    });
    log(`PUT /api/courses/${courseId}/outline`, outlineRes);
    if (outlineRes.ok) {
      logDetail("Nodes upserted", String((outlineRes.data as any).count));
    }
  }

  // Step 4: Verify outline was saved
  console.log("\n--- Step 4: Verify Outline ---");
  const getOutlineRes = await api("GET", `/api/courses/${courseId}/outline`);
  log(`GET /api/courses/${courseId}/outline`, getOutlineRes);
  if (getOutlineRes.ok) {
    const nodes = getOutlineRes.data as any[];
    logDetail("Total nodes", String(nodes.length));
    const kps = nodes.filter((n: any) => n.type === "knowledge_point");
    logDetail("Knowledge points", String(kps.length));
    knowledgePointIds = kps.map((n: any) => n.id);
    logDetail("Sample KP IDs", knowledgePointIds.slice(0, 3).join(", "));
  }

  // Step 5: Generate questions for the course
  console.log("\n--- Step 5: Generate Questions ---");
  const genRes = await api("POST", `/api/courses/${courseId}/generate-questions`);
  log(`POST /api/courses/${courseId}/generate-questions`, genRes);
  if (genRes.ok) {
    logDetail("Generated", String((genRes.data as any).generated));
    logDetail("KPs covered", String((genRes.data as any).kps_covered));
    logDetail("KPs remaining", String((genRes.data as any).kps_remaining));
  }

  // Step 6: Fetch questions
  console.log("\n--- Step 6: Fetch Questions ---");
  const qRes = await api("GET", `/api/questions?courseId=${courseId}`);
  log(`GET /api/questions?courseId=${courseId}`, qRes);
  if (qRes.ok) {
    const questions = qRes.data as any[];
    logDetail("Total questions", String(questions.length));
    if (questions.length > 0) {
      logDetail("Sample question type", questions[0].type);
      logDetail("Sample stem", questions[0].stem?.slice(0, 80) + "...");
      questionIds = questions.map((q: any) => q.id);
    }
  }
}

// ─── Scenario 2: Midterm Exam ──────────────────────
async function scenario2_midtermExam() {
  console.log("\n═══ Scenario 2: Midterm Exam Prep ═══\n");

  if (!courseId) {
    console.log("✗ No course ID — scenario 1 must run first");
    return;
  }

  const examScopeText = `Our 3rd midterm is on Friday, April 10th. The topics covered for this exam include:

5.3 Error bounds using improper integral: Be able to determine upper and lower bounds for the error in estimating the value of a convergent series using improper integrals. Similarly be able to estimate the value of the series. Be able to determine the number of terms necessary to ensure a certain error bound.

5.5 Alternating Series: Determine if an alternating series converges using the alternating series test. Recognizing that the A.S.T. does not indicate divergence. Determining if an Alt series converges absolutely, converges conditionally, or diverges. Be able to estimate the error in using N terms of a convergent alt series and find the number of terms needed.

5.6 Ratio and Root Tests: Be able to recognize when and how to apply the Ratio/Root tests. If either of these are inconclusive, finding a secondary test from Ch 5 that is useful.

5.7 Convergence testing for series: This is a review of Chapter 5.

6.1 Power Series: Determine values of x for which a power series converges/diverges. Determine Radius/Intervals of Convergence, including testing endpoints. Give a series representation of a function by rewriting in form 1/(1-x).

6.2 Properties of Power Series: Understand how adding, composing, multiplying by x^m affect interval of convergence. Take term-by-term derivatives and integrals of a power series.

6.3 Taylor and Maclaurin Series: Be able to find terms of a Taylor/Maclaurin series for a given function. Error/Sum bounds.`;

  // Step 1: Create exam date
  console.log("--- Step 1: Create Exam Date ---");
  const examRes = await api("POST", `/api/courses/${courseId}/exams`, {
    title: "Midterm 3",
    exam_date: "2026-04-10",
    knowledge_point_ids: knowledgePointIds.slice(0, 10), // link first 10 KPs
  });
  log(`POST /api/courses/${courseId}/exams`, examRes);
  if (examRes.ok) {
    logDetail("Exam ID", (examRes.data as any).id);
    logDetail("Exam date", (examRes.data as any).exam_date);
  }

  // Step 2: Match exam scope to knowledge points
  console.log("\n--- Step 2: Match Exam Scope → KPs ---");
  const scopeRes = await api("POST", `/api/courses/${courseId}/exam-scope`, {
    scope_text: examScopeText,
  });
  log(`POST /api/courses/${courseId}/exam-scope`, scopeRes);
  if (scopeRes.ok) {
    const scope = scopeRes.data as any;
    logDetail("Matched KPs", `${scope.matched_count}/${scope.total_kps}`);
    logDetail("Matched titles", (scope.matched_kp_titles ?? []).slice(0, 5).join(", "));
  }

  // Step 3: Generate exam prep questions
  console.log("\n--- Step 3: Generate Exam Prep Questions ---");
  const prepRes = await api("POST", `/api/courses/${courseId}/exam-prep`, {
    scope_text: examScopeText,
  });
  log(`POST /api/courses/${courseId}/exam-prep`, prepRes);
  if (prepRes.ok) {
    const prep = prepRes.data as any;
    logDetail("Topics found", String(prep.topics_found));
    logDetail("Topics processed", String(prep.topics_processed));
    logDetail("Questions generated", String(prep.questions_generated));
    if (prep.topics_failed?.length > 0) {
      logDetail("Topics failed", prep.topics_failed.join(", "));
    }
  }

  // Step 4: Fetch updated questions
  console.log("\n--- Step 4: Fetch All Questions ---");
  const qRes = await api("GET", `/api/questions?courseId=${courseId}`);
  log(`GET /api/questions?courseId=${courseId}`, qRes);
  if (qRes.ok) {
    const questions = qRes.data as any[];
    logDetail("Total questions now", String(questions.length));
    questionIds = questions.map((q: any) => q.id);

    // Show breakdown by type
    const byType: Record<string, number> = {};
    for (const q of questions) {
      byType[q.type] = (byType[q.type] ?? 0) + 1;
    }
    logDetail("By type", JSON.stringify(byType));
  }
}

// ─── Scenario 3: Answer Questions + Mastery ────────
async function scenario3_answerAndMastery() {
  console.log("\n═══ Scenario 3: Answer Questions + Check Mastery ═══\n");

  if (questionIds.length === 0) {
    console.log("✗ No questions — previous scenarios must run first");
    return;
  }

  // Fetch a question with its answer (we need to get answers from admin)
  const { data: fullQ } = await supabaseAdmin
    .from("questions")
    .select("id, type, stem, options, correct_answer, difficulty, knowledge_point_id")
    .eq("course_id", courseId)
    .limit(3);

  if (!fullQ || fullQ.length === 0) {
    console.log("✗ No questions found in database");
    return;
  }

  for (const q of fullQ) {
    console.log(`\n--- Answering: ${q.stem?.slice(0, 60)}... ---`);
    logDetail("Type", q.type);
    logDetail("Correct answer", q.correct_answer);

    // Submit correct answer
    const attemptRes = await api("POST", "/api/attempts", {
      question_id: q.id,
      user_answer: q.correct_answer,
    });
    log("POST /api/attempts (correct answer)", attemptRes);
    if (attemptRes.ok) {
      const attempt = attemptRes.data as any;
      logDetail("Is correct", String(attempt.is_correct));
      logDetail("Explanation", (attempt.explanation ?? "none").slice(0, 80));
    }
  }

  // Submit a wrong answer
  if (fullQ[0]) {
    console.log("\n--- Submitting Wrong Answer ---");
    const wrongRes = await api("POST", "/api/attempts", {
      question_id: fullQ[0].id,
      user_answer: "DEFINITELY_WRONG_ANSWER_XYZ",
    });
    log("POST /api/attempts (wrong answer)", wrongRes);
    if (wrongRes.ok) {
      logDetail("Is correct", String((wrongRes.data as any).is_correct));
    }
  }

  // Check mastery
  console.log("\n--- Check Mastery ---");
  const masteryRes = await api("GET", `/api/courses/${courseId}/mastery`);
  log(`GET /api/courses/${courseId}/mastery`, masteryRes);
  if (masteryRes.ok) {
    const mastery = masteryRes.data as any[];
    logDetail("Mastery records", String(mastery.length));
    if (mastery.length > 0) {
      logDetail("Sample", JSON.stringify(mastery[0]));
    }
  }
}

// ─── Cleanup ───────────────────────────────────────
async function cleanup() {
  console.log("\n═══ Cleanup ═══");
  if (courseId) {
    const delRes = await api("DELETE", `/api/courses/${courseId}`);
    log(`DELETE /api/courses/${courseId}`, delRes);
  }
}

// ─── Main ──────────────────────────────────────────
async function main() {
  console.log("╔══════════════════════════════════════════╗");
  console.log("║  CourseHub E2E Backend Test              ║");
  console.log("║  Base URL: " + BASE.padEnd(30) + "║");
  console.log("╚══════════════════════════════════════════╝");

  try {
    await setupAuth();
    await scenario1_fullOutline();
    await scenario2_midtermExam();
    await scenario3_answerAndMastery();
  } catch (err) {
    console.error("\n✗ FATAL:", (err as Error).message);
  } finally {
    await cleanup();
  }

  console.log("\n═══ Done ═══");
}

main();
