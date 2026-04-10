/**
 * E2E Backend Test — Tests all 34 API routes with real Supabase auth
 *
 * Scenario 1:  Create course → Parse Calculus II outline → Generate questions
 * Scenario 2:  Midterm exam → Scope matching → Exam prep questions
 * Scenario 3:  Answer questions → Check mastery
 * Scenario 4:  Bookmarks CRUD → Chat (streaming) → Exams
 * Scenario 5:  Course CRUD → Outline node CRUD → Study task update
 * Scenario 6:  Share token → Fork course → Revoke share
 * Scenario 7:  Generate lesson (AI) → Chunks → Progress tracking
 * Scenario 8:  Organize notes (AI) → Save note
 * Scenario 9:  Feedback → Quality check → Mistake patterns → Anki export → Delete exam
 * Scenario 10: Upload → Extract (AI) → Preview (AI)
 * Scenario 11: Generate study tasks → Regenerate (DESTRUCTIVE — runs last)
 *
 * Usage: SUPABASE_URL=... SUPABASE_KEY=... npx tsx tests/e2e-backend.ts
 */

import { createClient } from "@supabase/supabase-js";
import { readFileSync } from "node:fs";
import { join } from "node:path";

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
let examId = "";
let studyTaskIds: string[] = [];
let lessonId = "";
let shareToken = "";
let forkedCourseId = "";

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
    examId = (examRes.data as any).id;
    logDetail("Exam ID", examId);
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

  // Step 3: Generate exam prep questions (6 topics × 3 parallel = ~60-90s AI)
  console.log("\n--- Step 3: Generate Exam Prep Questions ---");
  const prepRes = await api("POST", `/api/courses/${courseId}/exam-prep`, {
    scope_text: examScopeText,
  }, 180_000);
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

  // Fetch questions with non-empty answers via admin (API hides answer field)
  const { data: allQ } = await supabaseAdmin
    .from("questions")
    .select("id, type, stem, options, answer, difficulty, knowledge_point_id")
    .eq("course_id", courseId)
    .not("answer", "is", null)
    .neq("answer", "")
    .limit(3);
  const fullQ = allQ;

  if (!fullQ || fullQ.length === 0) {
    console.log("✗ No questions with answers in DB");
    return;
  }

  for (const q of fullQ) {
    console.log(`\n--- Answering: ${q.stem?.slice(0, 60)}... ---`);
    logDetail("Type", q.type);
    logDetail("Correct answer", q.answer);

    // Submit correct answer
    const attemptRes = await api("POST", "/api/attempts", {
      question_id: q.id,
      user_answer: q.answer,
    });
    log("POST /api/attempts (correct)", attemptRes);
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
    log("POST /api/attempts (wrong)", wrongRes);
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

// ─── Scenario 4: Bookmarks + Chat + Exams (non-destructive) ───
async function scenario4_bookmarksAndTasks() {
  console.log("\n═══ Scenario 4: Bookmarks + Chat + Exams ═══\n");

  if (!courseId || questionIds.length === 0) {
    console.log("✗ No course/questions — previous scenarios must run first");
    return;
  }

  // Bookmark a question
  console.log("--- Step 1: Bookmark a Question ---");
  const bookmarkRes = await api("POST", "/api/bookmarks", {
    question_id: questionIds[0],
    note: "Review this before midterm",
  });
  log("POST /api/bookmarks", bookmarkRes);

  // Get bookmarks
  console.log("\n--- Step 2: Get Bookmarks ---");
  const getBookmarks = await api("GET", "/api/bookmarks");
  log("GET /api/bookmarks", getBookmarks);
  if (getBookmarks.ok) {
    logDetail("Bookmarks count", String((getBookmarks.data as any[]).length));
  }

  // Delete bookmark
  console.log("\n--- Step 3: Delete Bookmark ---");
  const delBookmark = await api("DELETE", "/api/bookmarks", {
    question_id: questionIds[0],
  });
  log("DELETE /api/bookmarks", delBookmark);

  // Chat with course AI — streaming response, just verify status + first chunk
  console.log("\n--- Step 4: Chat (streaming) ---");
  try {
    const chatRes = await fetch(`${BASE}/api/courses/${courseId}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Cookie: cookie() },
      body: JSON.stringify({
        messages: [{ id: "msg-1", role: "user", parts: [{ type: "text", text: "What is integration by parts?" }] }],
      }),
      signal: AbortSignal.timeout(60_000),
    });
    const streamOk = chatRes.ok && (chatRes.headers.get("content-type") ?? "").includes("text/event-stream");
    console.log(`${streamOk ? "\x1b[32m✓" : "\x1b[31m✗"}\x1b[0m [${chatRes.status}] POST /api/courses/${courseId}/chat`);
    if (streamOk) {
      // Consume first chunk to verify stream works
      const reader = chatRes.body?.getReader();
      if (reader) {
        const { value } = await reader.read();
        logDetail("First chunk", `${value?.byteLength ?? 0} bytes`);
        reader.cancel();
      }
    } else if (!chatRes.ok) {
      const errText = await chatRes.text();
      console.log(`  Error: ${errText.slice(0, 200)}`);
    }
  } catch (err) {
    console.log(`\x1b[31m✗\x1b[0m [0] POST chat — ${(err as Error).message}`);
  }

  // Get exams list
  console.log("\n--- Step 5: Get Exams ---");
  const examsRes = await api("GET", `/api/courses/${courseId}/exams`);
  log(`GET /api/courses/${courseId}/exams`, examsRes);
  if (examsRes.ok) {
    logDetail("Exams count", String((examsRes.data as any[]).length));
  }
}

// ─── Scenario 5: Course CRUD + Outline Node CRUD ───
async function scenario5_crudOperations() {
  console.log("\n═══ Scenario 5: Course CRUD + Outline Node CRUD ═══\n");

  if (!courseId) {
    console.log("✗ No course — previous scenarios must run first");
    return;
  }

  // List courses
  console.log("--- Step 1: List Courses ---");
  const listRes = await api("GET", "/api/courses");
  log("GET /api/courses", listRes);
  if (listRes.ok) {
    logDetail("Courses count", String((listRes.data as any[]).length));
  }

  // Get single course
  console.log("\n--- Step 2: Get Single Course ---");
  const getRes = await api("GET", `/api/courses/${courseId}`);
  log(`GET /api/courses/${courseId}`, getRes);
  if (getRes.ok) {
    logDetail("Title", (getRes.data as any).title);
    logDetail("Status", (getRes.data as any).status);
  }

  // Update course
  console.log("\n--- Step 3: Update Course ---");
  const patchRes = await api("PATCH", `/api/courses/${courseId}`, {
    description: "Updated: Integral calculus, sequences, series, and more",
  });
  log(`PATCH /api/courses/${courseId}`, patchRes);

  // Create outline node
  console.log("\n--- Step 4: Create Outline Node ---");
  const parentId = knowledgePointIds.length > 0
    ? null // top-level node
    : null;
  const createNodeRes = await api("POST", "/api/outline-nodes", {
    course_id: courseId,
    title: "E2E Test Chapter",
    type: "chapter",
    parent_id: parentId,
    content: "Test content for CRUD verification",
  });
  log("POST /api/outline-nodes", createNodeRes);
  let testNodeId = "";
  if (createNodeRes.ok) {
    testNodeId = (createNodeRes.data as any).id;
    logDetail("Node ID", testNodeId);
  }

  // Update outline node
  if (testNodeId) {
    console.log("\n--- Step 5: Update Outline Node ---");
    const patchNodeRes = await api("PATCH", `/api/outline-nodes/${testNodeId}`, {
      title: "E2E Test Chapter (Renamed)",
      content: "Updated content",
    });
    log(`PATCH /api/outline-nodes/${testNodeId}`, patchNodeRes);

    // Delete outline node
    console.log("\n--- Step 6: Delete Outline Node ---");
    const delNodeRes = await api("DELETE", `/api/outline-nodes/${testNodeId}`);
    log(`DELETE /api/outline-nodes/${testNodeId}`, delNodeRes);
  }

  // Insert a study task via admin (since /generate is now deferred to scenario 11)
  console.log("\n--- Step 7: Update Study Task Status ---");
  const { data: inserted } = await supabaseAdmin
    .from("study_tasks")
    .insert({
      course_id: courseId,
      knowledge_point_id: knowledgePointIds[0] ?? null,
      title: "E2E Test Study Task",
      description: "Placeholder for PATCH test",
      task_type: "read",
      priority: 1,
      order: 0,
    })
    .select("id")
    .single();
  if (inserted) {
    const taskId = inserted.id;
    studyTaskIds.push(taskId);
    const patchTaskRes = await api("PATCH", `/api/study-tasks/${taskId}`, {
      status: "done",
    });
    log(`PATCH /api/study-tasks/${taskId}`, patchTaskRes);
  } else {
    console.log("  ⚠ Failed to insert test study task via admin");
  }
}

// ─── Scenario 6: Share + Fork ──────────────────────
async function scenario6_shareAndFork() {
  console.log("\n═══ Scenario 6: Share + Fork ═══\n");

  if (!courseId) {
    console.log("✗ No course — previous scenarios must run first");
    return;
  }

  // Generate share token
  console.log("--- Step 1: Generate Share Token ---");
  const shareRes = await api("POST", `/api/courses/${courseId}/share`);
  log(`POST /api/courses/${courseId}/share`, shareRes);
  if (shareRes.ok) {
    shareToken = (shareRes.data as any).token;
    logDetail("Token", shareToken);
  }

  // Fork the course
  if (shareToken) {
    console.log("\n--- Step 2: Fork Course ---");
    const forkRes = await api("POST", "/api/courses/fork", {
      token: shareToken,
    });
    log("POST /api/courses/fork", forkRes);
    if (forkRes.ok) {
      forkedCourseId = (forkRes.data as any).course_id;
      logDetail("Forked course ID", forkedCourseId);
    }
  }

  // Revoke share token
  console.log("\n--- Step 3: Revoke Share Token ---");
  const revokeRes = await api("DELETE", `/api/courses/${courseId}/share`);
  log(`DELETE /api/courses/${courseId}/share`, revokeRes);
}

// ─── Scenario 7: Lesson Pipeline (AI) ─────────────
async function scenario7_lessons() {
  console.log("\n═══ Scenario 7: Lesson Pipeline (AI) ═══\n");

  if (!courseId || knowledgePointIds.length === 0) {
    console.log("✗ No course/KPs — previous scenarios must run first");
    return;
  }

  // Generate one lesson (non-streaming, ~20s)
  console.log("--- Step 1: Generate Single Lesson ---");
  const genRes = await api("POST", `/api/courses/${courseId}/lessons/generate-one`, {
    knowledge_point_id: knowledgePointIds[0],
    stream: false,
  });
  log(`POST /api/courses/${courseId}/lessons/generate-one`, genRes);
  if (genRes.ok) {
    lessonId = (genRes.data as any).lesson_id;
    logDetail("Lesson ID", lessonId);
    logDetail("Chunks generated", String((genRes.data as any).chunks_generated));
  }

  // List lessons
  console.log("\n--- Step 2: List Lessons ---");
  const listRes = await api("GET", `/api/courses/${courseId}/lessons`);
  log(`GET /api/courses/${courseId}/lessons`, listRes);
  if (listRes.ok) {
    const lessons = listRes.data as any[];
    logDetail("Lessons count", String(lessons.length));
    if (!lessonId && lessons.length > 0) {
      lessonId = lessons[0].id;
    }
  }

  // Get lesson chunks
  if (lessonId) {
    console.log("\n--- Step 3: Get Lesson Chunks ---");
    const chunksRes = await api("GET", `/api/courses/${courseId}/lessons/${lessonId}/chunks`);
    log(`GET /api/courses/${courseId}/lessons/${lessonId}/chunks`, chunksRes);
    if (chunksRes.ok) {
      const chunks = chunksRes.data as any[];
      logDetail("Chunks count", String(chunks.length));
      if (chunks.length > 0) {
        logDetail("First chunk type", chunks[0].checkpoint_type ?? "none");
      }
    }

    // Track progress
    console.log("\n--- Step 4: Track Lesson Progress ---");
    const progressRes = await api("POST", `/api/courses/${courseId}/lessons/${lessonId}/progress`, {
      completed: false,
      lastChunkIndex: 1,
      checkpointResults: { 0: { correct: true, answer: "B" } },
    });
    log(`POST /api/courses/${courseId}/lessons/${lessonId}/progress`, progressRes);
  }
}

// ─── Scenario 8: Notes Pipeline (AI) ──────────────
async function scenario8_notes() {
  console.log("\n═══ Scenario 8: Notes Pipeline (AI) ═══\n");

  if (!courseId) {
    console.log("✗ No course — previous scenarios must run first");
    return;
  }

  // Organize a voice transcript
  console.log("--- Step 1: Organize Study Note (AI) ---");
  const organizeRes = await api("POST", `/api/courses/${courseId}/notes/organize`, {
    transcript: "Today we covered integration by parts. The formula is integral of u dv equals uv minus integral of v du. The key is choosing u and dv wisely. LIATE rule helps: Logarithmic, Inverse trig, Algebraic, Trig, Exponential. Professor said this will be on the midterm for sure. I'm confused about when to use tabular integration versus regular integration by parts.",
    source: "voice",
  });
  log(`POST /api/courses/${courseId}/notes/organize`, organizeRes);
  let organized: any = null;
  if (organizeRes.ok) {
    organized = (organizeRes.data as any).note;
    logDetail("Title", organized?.title ?? "N/A");
    logDetail("Key points", String(organized?.key_points?.length ?? 0));
    logDetail("Clarification Qs", String(organized?.clarification_questions?.length ?? 0));
    logDetail("Matched KP", organized?.matched_knowledge_point_title ?? "none");
  }

  // Create the note (save to DB)
  if (organized) {
    console.log("\n--- Step 2: Save Note to DB ---");
    const noteRes = await api("POST", `/api/courses/${courseId}/notes`, {
      knowledge_point_id: null,
      raw_transcript: "Today we covered integration by parts...",
      source: "voice",
      title: organized.title ?? "Integration by Parts Notes",
      summary: organized.summary ?? "Notes on integration by parts technique",
      key_points: organized.key_points ?? ["LIATE rule for choosing u"],
      confusing_points: organized.confusing_points ?? [],
      next_action: organized.next_action ?? null,
      clarification_questions: organized.clarification_questions ?? [],
      clarification_answers: [],
    });
    log(`POST /api/courses/${courseId}/notes`, noteRes);
  }
}

// ─── Scenario 9: Quality + Analytics + Misc ───────
async function scenario9_qualityAndAnalytics() {
  console.log("\n═══ Scenario 9: Quality + Analytics + Misc ═══\n");

  if (!courseId) {
    console.log("✗ No course — previous scenarios must run first");
    return;
  }

  // Re-fetch question IDs directly from DB to ensure freshness
  // (avoids staleness if previous scenarios mutated questions)
  const { data: freshQs } = await supabaseAdmin
    .from("questions")
    .select("id")
    .eq("course_id", courseId)
    .limit(5);
  if (freshQs && freshQs.length > 0) {
    questionIds = freshQs.map((q: any) => q.id);
    logDetail("Re-fetched question IDs", String(questionIds.length));
  } else {
    console.log("✗ No questions in DB — skipping quality/analytics tests");
    return;
  }

  // Submit feedback on a question (wrong_answer x2 to trigger auto-flag)
  console.log("\n--- Step 1: Submit Question Feedback ---");
  const fb1 = await api("POST", `/api/questions/${questionIds[0]}/feedback`, {
    reason: "wrong_answer",
  });
  log(`POST /api/questions/${questionIds[0]}/feedback (#1)`, fb1);
  if (fb1.ok) {
    logDetail("Auto flagged", String((fb1.data as any).auto_flagged));
  }

  const fb2 = await api("POST", `/api/questions/${questionIds[0]}/feedback`, {
    reason: "wrong_answer",
  });
  log(`POST /api/questions/${questionIds[0]}/feedback (#2)`, fb2);
  if (fb2.ok) {
    logDetail("Auto flagged", String((fb2.data as any).auto_flagged));
  }

  // Also submit different feedback types
  if (questionIds.length > 1) {
    const fb3 = await api("POST", `/api/questions/${questionIds[1]}/feedback`, {
      reason: "too_hard",
    });
    log(`POST /api/questions/${questionIds[1]}/feedback (too_hard)`, fb3);
  }

  // Quality check
  console.log("\n--- Step 2: Quality Check ---");
  const qcRes = await api("POST", "/api/questions/quality-check", {
    courseId,
  });
  log("POST /api/questions/quality-check", qcRes);
  if (qcRes.ok) {
    const qc = qcRes.data as any;
    logDetail("Checked", String(qc.checked));
    logDetail("Flagged", String(qc.flagged));
  }

  // Mistake patterns
  console.log("\n--- Step 3: Mistake Patterns ---");
  const mpRes = await api("GET", `/api/courses/${courseId}/mistake-patterns`);
  log(`GET /api/courses/${courseId}/mistake-patterns`, mpRes);
  if (mpRes.ok) {
    const patterns = mpRes.data as any[];
    logDetail("Weak KPs", String(patterns.length));
    if (patterns.length > 0) {
      logDetail("Worst KP", `${patterns[0].kp_title} (${(patterns[0].error_rate * 100).toFixed(0)}% error)`);
    }
  }

  // Export Anki
  console.log("\n--- Step 4: Export Anki ---");
  const ankiRes = await api("GET", `/api/courses/${courseId}/export-anki`);
  log(`GET /api/courses/${courseId}/export-anki`, ankiRes);
  if (ankiRes.ok) {
    const text = typeof ankiRes.data === "string" ? ankiRes.data : JSON.stringify(ankiRes.data);
    logDetail("Export size", `${text.length} chars`);
    logDetail("Lines", String(text.split("\n").length));
  }

  // Delete exam
  if (examId) {
    console.log("\n--- Step 5: Delete Exam ---");
    const delExamRes = await api("DELETE", `/api/courses/${courseId}/exams`, {
      exam_id: examId,
    });
    log(`DELETE /api/courses/${courseId}/exams`, delExamRes);
  }
}

// ─── Scenario 10: Upload + Extract + Preview ──────
async function scenario10_uploadAndPreview() {
  console.log("\n═══ Scenario 10: Upload + Extract + Preview ═══\n");

  if (!courseId) {
    console.log("✗ No course — previous scenarios must run first");
    return;
  }

  // Upload a real PDF fixture (generated via matplotlib, has readable text for AI vision)
  console.log("--- Step 1: Upload File ---");
  let uploadPath = "";
  let uploadId = "";
  try {
    const pdfPath = join(process.cwd(), "tests/fixtures/test-notes.pdf");
    const pdfBytes = readFileSync(pdfPath);
    const blob = new Blob([new Uint8Array(pdfBytes)], { type: "application/pdf" });
    const form = new FormData();
    form.append("file", blob, "test-notes.pdf");
    form.append("courseId", courseId);

    const uploadRes = await fetch(`${BASE}/api/upload`, {
      method: "POST",
      headers: { Cookie: cookie() },
      body: form,
      signal: AbortSignal.timeout(30_000),
    });
    const uploadData = await uploadRes.json();
    const result = { status: uploadRes.status, data: uploadData, ok: uploadRes.ok };
    log("POST /api/upload", result);
    if (result.ok) {
      uploadPath = uploadData.storagePath ?? "";
      uploadId = uploadData.upload?.id ?? "";
      logDetail("Storage path", uploadPath);
    }
  } catch (err) {
    console.log(`  ✗ Upload failed: ${(err as Error).message}`);
  }

  // List uploads
  console.log("\n--- Step 2: List Uploads ---");
  const uploadsRes = await api("GET", `/api/courses/${courseId}/uploads`);
  log(`GET /api/courses/${courseId}/uploads`, uploadsRes);
  if (uploadsRes.ok) {
    const uploads = uploadsRes.data as any[];
    logDetail("Uploads count", String(uploads.length));
    if (!uploadId && uploads.length > 0) uploadId = uploads[0].id;
  }

  // Extract content from uploaded PDF (AI vision)
  if (uploadPath) {
    console.log("\n--- Step 3: Extract Content (AI) ---");
    const extractRes = await api("POST", `/api/courses/${courseId}/extract`, {
      storagePath: uploadPath,
    });
    log(`POST /api/courses/${courseId}/extract`, extractRes);
    if (extractRes.ok) {
      const sections = (extractRes.data as any).sections ?? [];
      logDetail("Sections extracted", String(sections.length));
    }
  }

  // Delete upload
  if (uploadId) {
    console.log("\n--- Step 4: Delete Upload ---");
    const delUploadRes = await api("DELETE", `/api/courses/${courseId}/uploads`, {
      upload_id: uploadId,
    });
    log(`DELETE /api/courses/${courseId}/uploads`, delUploadRes);
  }

  // Preview learning (AI, rate-limited)
  console.log("\n--- Step 5: Preview Learning (AI) ---");
  const previewRes = await api("POST", "/api/preview/learning", {
    title: "Quick Calculus Preview",
    nodes: [
      {
        title: "Integration by Parts",
        type: "topic",
        content: null,
        children: [
          { title: "LIATE Rule", type: "knowledge_point", content: "Choosing u and dv", children: [] },
          { title: "Tabular Method", type: "knowledge_point", content: "Repeated integration by parts", children: [] },
        ],
      },
    ],
  });
  log("POST /api/preview/learning", previewRes);
  if (previewRes.ok) {
    const preview = previewRes.data as any;
    logDetail("Study targets", String(preview.study_targets_used));
    logDetail("Tasks", String(preview.tasks?.length ?? 0));
    logDetail("Questions", String(preview.questions?.length ?? 0));
  }
}

// ─── Scenario 11: Destructive — Generate + Regenerate ───
// These endpoints delete auto-generated questions, so they run AFTER
// all question-dependent scenarios (9 uses questions, 10 is independent).
async function scenario11_generateAndRegenerate() {
  console.log("\n═══ Scenario 11: Generate Study Tasks + Regenerate (destructive) ═══\n");

  if (!courseId) {
    console.log("✗ No course — previous scenarios must run first");
    return;
  }

  // Generate study tasks (deletes auto-questions, creates tasks)
  console.log("--- Step 1: Generate Study Tasks ---");
  const genRes = await api("POST", `/api/courses/${courseId}/generate`, {
    language: "en",
  });
  log(`POST /api/courses/${courseId}/generate`, genRes);
  if (genRes.ok) {
    const gen = genRes.data as any;
    logDetail("Tasks generated", String(gen.tasks_generated));
    logDetail("Questions generated", String(gen.questions_generated));
  }

  // Regenerate in Chinese (translates outline + regenerates tasks/questions, slow)
  console.log("\n--- Step 2: Regenerate in Chinese (AI, may take 3-5min) ---");
  const regenRes = await api("POST", `/api/courses/${courseId}/regenerate`, {
    language: "zh",
  }, 420_000); // 7 min timeout — translates 30+ KPs + 2 parallel AI regens
  log(`POST /api/courses/${courseId}/regenerate`, regenRes);
  if (regenRes.ok) {
    const regen = regenRes.data as any;
    logDetail("Translated nodes", String(regen.translated_nodes));
    logDetail("Tasks generated", String(regen.tasks_generated));
    logDetail("Questions generated", String(regen.questions_generated));
  }
}

// ─── Cleanup ───────────────────────────────────────
async function cleanup() {
  console.log("\n═══ Cleanup ═══");
  // Use admin client to bypass RLS and expired JWTs
  // (test runtime can exceed JWT expiration on multi-AI scenarios)
  if (forkedCourseId) {
    const { error } = await supabaseAdmin.from("courses").delete().eq("id", forkedCourseId);
    console.log(error ? `\x1b[31m✗\x1b[0m Failed to delete forked course: ${error.message}` : `\x1b[32m✓\x1b[0m Deleted forked course ${forkedCourseId}`);
  }
  if (courseId) {
    const { error } = await supabaseAdmin.from("courses").delete().eq("id", courseId);
    console.log(error ? `\x1b[31m✗\x1b[0m Failed to delete course: ${error.message}` : `\x1b[32m✓\x1b[0m Deleted course ${courseId}`);
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
    await scenario4_bookmarksAndTasks();
    await scenario5_crudOperations();
    await scenario6_shareAndFork();
    await scenario7_lessons();
    await scenario8_notes();
    await scenario9_qualityAndAnalytics();
    await scenario10_uploadAndPreview();
    await scenario11_generateAndRegenerate();
  } catch (err) {
    console.error("\n✗ FATAL:", (err as Error).message);
  } finally {
    await cleanup();
  }

  console.log("\n═══ Done ═══");
}

main();
