import { createClient } from "@/lib/supabase/server";
import { generateLessonChunks } from "@/lib/ai";
import { NextResponse } from "next/server";

export const maxDuration = 60;

// Generate a lesson with interactive chunks for ONE knowledge point
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { knowledge_point_id } = await request.json();
  if (!knowledge_point_id) return NextResponse.json({ error: "knowledge_point_id required" }, { status: 400 });

  // Check if lesson already exists
  const { data: existingLesson } = await supabase
    .from("lessons")
    .select("id")
    .eq("course_id", id)
    .eq("knowledge_point_id", knowledge_point_id)
    .limit(1)
    .single();

  if (existingLesson) {
    return NextResponse.json({ lesson_id: existingLesson.id, cached: true });
  }

  // Get course + knowledge point info
  const { data: course } = await supabase.from("courses").select("title, description").eq("id", id).single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  const { data: kp } = await supabase
    .from("outline_nodes")
    .select("title, content")
    .eq("id", knowledge_point_id)
    .single();

  if (!kp) return NextResponse.json({ error: "Knowledge point not found" }, { status: 404 });

  // Generate outline + chunks in parallel
  const { outline, chunks } = await generateLessonChunks(
    course.title,
    { title: kp.title, content: kp.content },
    course.description ?? "",
  );

  // Insert lesson
  const { data: lesson, error: lessonError } = await supabase
    .from("lessons")
    .insert({
      course_id: id,
      knowledge_point_id,
      title: kp.title,
      content: chunks.map(c => c.content).join("\n\n---\n\n"), // fallback monolithic content
      key_takeaways: outline.map(o => o.teaching_goal),
      examples: [],
      order: 0,
    })
    .select()
    .single();

  if (lessonError) return NextResponse.json({ error: lessonError.message }, { status: 500 });

  // Insert chunks
  const chunkRows = chunks.map(c => ({
    lesson_id: lesson.id,
    chunk_index: c.chunk_index,
    content: c.content,
    checkpoint_type: c.checkpoint_type,
    checkpoint_prompt: c.checkpoint_prompt,
    checkpoint_answer: c.checkpoint_answer,
    checkpoint_options: c.checkpoint_options,
    // remediation fields left NULL — generated on-demand
    widget_code: null,
    widget_description: null,
    widget_challenge: null,
    checkpoint_core_elements: null,
    remediation_content: null,
    remediation_question: null,
    remediation_answer: null,
  }));

  await supabase.from("lesson_chunks").insert(chunkRows);

  return NextResponse.json({
    lesson_id: lesson.id,
    chunks_generated: chunks.length,
    outline,
  });
}
