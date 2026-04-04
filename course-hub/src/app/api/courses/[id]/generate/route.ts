import { createClient } from "@/lib/supabase/server";
import { generateStudyTasks, generateQuestionsFromOutline } from "@/lib/ai";
import { NextResponse } from "next/server";

function selectStudyTargets(nodes: { id: string; title: string; content: string | null; type: string; parent_id: string | null }[]) {
  const knowledgePoints = nodes.filter((n) => n.type === "knowledge_point");
  if (knowledgePoints.length > 0) {
    return knowledgePoints.map((n) => ({ id: n.id, title: n.title, content: n.content }));
  }

  const parentIds = new Set(nodes.map((n) => n.parent_id).filter(Boolean));
  const leafNodes = nodes.filter((n) => !parentIds.has(n.id));
  if (leafNodes.length > 0) {
    return leafNodes.map((n) => ({ id: n.id, title: n.title, content: n.content }));
  }

  return nodes.map((n) => ({ id: n.id, title: n.title, content: n.content }));
}

export async function POST(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Get course
  const { data: course } = await supabase.from("courses").select("title").eq("id", id).single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  // Get knowledge points from outline
  const { data: allNodes } = await supabase
    .from("outline_nodes")
    .select("id, parent_id, title, content, type")
    .eq("course_id", id);

  const studyTargets = selectStudyTargets(allNodes ?? []);

  if (studyTargets.length === 0) {
    return NextResponse.json({ error: "No study targets found in outline" }, { status: 400 });
  }

  // Run both pipelines in parallel
  const [studyTasks, questions] = await Promise.all([
    generateStudyTasks(
      course.title,
      studyTargets.map((kp) => ({ title: kp.title, content: kp.content }))
    ),
    generateQuestionsFromOutline(
      course.title,
      studyTargets.map((kp) => ({ title: kp.title, content: kp.content }))
    ),
  ]);

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
