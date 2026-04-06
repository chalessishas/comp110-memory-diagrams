import { createClient } from "@/lib/supabase/server";
import { generateStudyTasks, generateQuestionsFromOutline } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

// Max knowledge points per AI call — 8 keeps within Vercel 60s function timeout
// (each AI call processes all KPs in one prompt, ~5-10s per 8 KPs)
const MAX_STUDY_TARGETS = 8;

function selectStudyTargets(nodes: { id: string; title: string; content: string | null; type: string; parent_id: string | null }[]) {
  const knowledgePoints = nodes.filter((n) => n.type === "knowledge_point");
  if (knowledgePoints.length > 0) {
    return knowledgePoints.slice(0, MAX_STUDY_TARGETS).map((n) => ({ id: n.id, title: n.title, content: n.content }));
  }

  const parentIds = new Set(nodes.map((n) => n.parent_id).filter(Boolean));
  const leafNodes = nodes.filter((n) => !parentIds.has(n.id));
  if (leafNodes.length > 0) {
    return leafNodes.slice(0, MAX_STUDY_TARGETS).map((n) => ({ id: n.id, title: n.title, content: n.content }));
  }

  return nodes.slice(0, MAX_STUDY_TARGETS).map((n) => ({ id: n.id, title: n.title, content: n.content }));
}

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  let language: string | undefined;
  try {
    const body = await request.json();
    language = body?.language;
  } catch {
    // No body is fine — fire-and-forget calls don't send body
  }

  // Dedup: max 1 generate per course per 30s
  if (!checkRateLimit(`generate:${id}`, 1, 30_000)) {
    return NextResponse.json({ error: "Generation already in progress" }, { status: 429 });
  }

  // Concurrency guard: use updated_at as a lightweight lock
  // Set a sentinel value; if another request already set it, bail out
  const lockTime = new Date().toISOString();
  const { data: lockResult } = await supabase
    .from("courses")
    .update({ updated_at: lockTime })
    .eq("id", id)
    .select("title")
    .single();

  if (!lockResult) return NextResponse.json({ error: "Course not found" }, { status: 404 });
  const course = lockResult;

  // Clear previously auto-generated tasks and questions (not exam-sourced ones)
  await supabase.from("study_tasks").delete().eq("course_id", id);
  await supabase.from("questions").delete().eq("course_id", id).is("source_upload_id", null);

  // Get knowledge points from outline
  const { data: allNodes } = await supabase
    .from("outline_nodes")
    .select("id, parent_id, title, content, type")
    .eq("course_id", id);

  const studyTargets = selectStudyTargets(allNodes ?? []);

  if (studyTargets.length === 0) {
    return NextResponse.json({ error: "No study targets found in outline" }, { status: 400 });
  }

  // Run sequentially to stay within Vercel function time limits
  // (parallel caused timeouts — two large AI calls competing for bandwidth)
  const kpData = studyTargets.map((kp) => ({ title: kp.title, content: kp.content }));

  let studyTasks: Awaited<ReturnType<typeof generateStudyTasks>> = [];
  try {
    studyTasks = await generateStudyTasks(course.title, kpData, language);
  } catch (e) {
    console.error("Study task generation failed:", e instanceof Error ? e.message : e);
  }

  let questions: Awaited<ReturnType<typeof generateQuestionsFromOutline>> = [];
  try {
    questions = await generateQuestionsFromOutline(course.title, kpData, language);
  } catch (e) {
    console.error("Question generation failed:", e instanceof Error ? e.message : e);
  }

  // Map KP titles to IDs
  const kpMap = new Map(studyTargets.map((kp) => [kp.title.toLowerCase(), kp.id]));

  // Insert study tasks
  const taskRows = studyTasks.map((task, i) => ({
    course_id: id,
    knowledge_point_id: kpMap.get(task.knowledge_point_title.toLowerCase()) ?? null,
    title: task.title,
    description: task.description,
    task_type: task.task_type,
    priority: task.priority,
    order: i,
  }));

  if (taskRows.length > 0) {
    await supabase.from("study_tasks").insert(taskRows);
  }

  // Insert questions
  const questionRows = questions.map((q) => ({
    course_id: id,
    type: q.type,
    stem: q.stem,
    options: q.options,
    answer: q.answer,
    explanation: q.explanation,
    difficulty: q.difficulty,
    knowledge_point_id: kpMap.get(q.matched_kp_title.toLowerCase()) ?? null,
  }));

  if (questionRows.length > 0) {
    await supabase.from("questions").insert(questionRows);
  }

  return NextResponse.json({
    tasks_generated: taskRows.length,
    questions_generated: questionRows.length,
    study_targets_used: studyTargets.length,
  });
}
