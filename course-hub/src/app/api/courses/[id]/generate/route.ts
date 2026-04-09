import { createClient } from "@/lib/supabase/server";
import { generateStudyTasks } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

// Max knowledge points per AI call — 5 keeps within Vercel 60s function timeout
// DashScope takes ~20-25s for 5 KPs with study tasks
const MAX_STUDY_TARGETS = 5;

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
  if (!await checkRateLimit(`generate:${id}`, 1, 30_000)) {
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

  // Only generate study tasks on course creation — questions generated on-demand
  // when user visits Practice tab (keeps within Vercel 60s function timeout)
  const kpData = studyTargets.map((kp) => ({ title: kp.title, content: kp.content }));

  let studyTasks: Awaited<ReturnType<typeof generateStudyTasks>> = [];
  let taskError: string | null = null;
  try {
    studyTasks = await generateStudyTasks(course.title, kpData, language);
  } catch (e) {
    taskError = e instanceof Error ? e.message : String(e);
    console.error("Study task generation failed:", taskError);
  }

  // Questions are NOT generated here — too slow for serverless.
  // They are generated on-demand via POST /api/courses/[id]/regenerate or Practice tab.
  const questions: { type: string; stem: string; options: unknown; answer: string; explanation: string | null; difficulty: number; matched_kp_title: string }[] = [];

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
    ...(taskError ? { task_error: taskError } : {}),
  });
}
