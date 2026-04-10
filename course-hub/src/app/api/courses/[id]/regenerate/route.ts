import { createClient } from "@/lib/supabase/server";
import { generateStudyTasks, generateQuestionsFromOutline, stripThinkBlocks, textModel } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  if (!await checkRateLimit(`regenerate:${user.id}`, 3, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded. Try again in a minute." }, { status: 429 });
  }

  const { language } = await request.json();
  const lang = language === "zh" ? "zh" : "en";

  const { data: course } = await supabase.from("courses").select("title, description").eq("id", id).eq("user_id", user.id).single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  // Get all outline nodes
  const { data: allNodes } = await supabase
    .from("outline_nodes")
    .select("id, parent_id, title, content, type")
    .eq("course_id", id);

  const knowledgePoints = (allNodes ?? []).filter((n) => n.type === "knowledge_point");
  if (knowledgePoints.length === 0) {
    return NextResponse.json({ error: "No knowledge points" }, { status: 400 });
  }

  // Step 1: Translate outline node titles and content via AI
  try {
    const { generateText } = await import("ai");

    const { text } = await generateText({
      model: textModel,
      timeout: 55_000,
      messages: [{
        role: "user",
        content: `Translate the following course outline nodes into ${lang === "zh" ? "Chinese (简体中文)" : "English"}. Return ONLY valid JSON (no markdown). Keep the same structure, just translate title and content fields.

Input:
${JSON.stringify(allNodes?.map(n => ({ id: n.id, title: n.title, content: n.content })))}

Return format: [{"id": "...", "title": "translated title", "content": "translated content or null"}]`,
      }],
    });

    const jsonMatch = stripThinkBlocks(text).match(/\[[\s\S]*\]/);
    if (jsonMatch) {
      const translated = JSON.parse(jsonMatch[0]) as { id: string; title: string; content: string | null }[];
      for (const node of translated) {
        await supabase.from("outline_nodes").update({ title: node.title, content: node.content }).eq("id", node.id);
      }
    }
  } catch {
    // Continue even if translation fails
  }

  // Step 2: Re-fetch translated nodes
  const { data: updatedNodes } = await supabase
    .from("outline_nodes")
    .select("id, parent_id, title, content, type")
    .eq("course_id", id);

  const updatedKPs = (updatedNodes ?? []).filter((n) => n.type === "knowledge_point");
  const kpData = updatedKPs.map((kp) => ({ title: kp.title, content: kp.content }));

  // Step 3: Clear and regenerate tasks + questions + lessons in target language
  await supabase.from("study_tasks").delete().eq("course_id", id);
  await supabase.from("questions").delete().eq("course_id", id).is("source_upload_id", null);
  await supabase.from("lessons").delete().eq("course_id", id);

  const [tasks, questions] = await Promise.all([
    generateStudyTasks(course.title, kpData, lang),
    generateQuestionsFromOutline(course.title, kpData, lang),
  ]);

  const kpMap = new Map(updatedKPs.map((kp) => [kp.title.toLowerCase(), kp.id]));

  if (tasks.length > 0) {
    await supabase.from("study_tasks").insert(
      tasks.map((t, i) => ({
        course_id: id,
        knowledge_point_id: kpMap.get(t.knowledge_point_title.toLowerCase()) ?? null,
        title: t.title,
        description: t.description,
        task_type: t.task_type,
        priority: t.priority,
        order: i,
      }))
    );
  }

  if (questions.length > 0) {
    await supabase.from("questions").insert(
      questions.map((q) => ({
        course_id: id,
        type: q.type,
        stem: q.stem,
        options: q.options,
        answer: q.answer,
        explanation: q.explanation,
        difficulty: q.difficulty,
        knowledge_point_id: kpMap.get(q.matched_kp_title.toLowerCase()) ?? null,
      }))
    );
  }

  return NextResponse.json({
    translated_nodes: updatedKPs.length,
    tasks_generated: tasks.length,
    questions_generated: questions.length,
    language: lang,
  });
}
