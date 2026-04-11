import { createClient } from "@/lib/supabase/server";
import { verifyCourseOwnership } from "@/lib/supabase/ownership";
import { NextResponse } from "next/server";

export async function GET(
  _: Request,
  { params }: { params: Promise<{ id: string; lessonId: string }> }
) {
  const { id, lessonId } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (!await verifyCourseOwnership(supabase, id, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // Verify lesson belongs to this course before returning chunks
  const { data: lessonCheck } = await supabase
    .from("lessons")
    .select("id")
    .eq("id", lessonId)
    .eq("course_id", id)
    .single();
  if (!lessonCheck) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { data, error } = await supabase
    .from("lesson_chunks")
    .select("*")
    .eq("lesson_id", lessonId)
    .order("chunk_index");

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // If no chunks exist, fall back to splitting the lesson's monolithic markdown by ## headers
  if (!data || data.length === 0) {
    const { data: lesson } = await supabase
      .from("lessons")
      .select("content, title")
      .eq("id", lessonId)
      .eq("course_id", id)
      .single();

    if (!lesson) return NextResponse.json([]);

    const sections = lesson.content.split(/(?=^## )/m).filter((s: string) => s.trim());
    const fallbackChunks = sections.map((content: string, i: number) => ({
      id: `fallback-${i}`,
      lesson_id: lessonId,
      chunk_index: i,
      content: content.trim(),
      widget_code: null,
      widget_description: null,
      widget_challenge: null,
      checkpoint_type: null,
      checkpoint_prompt: null,
      checkpoint_answer: null,
      checkpoint_options: null,
      checkpoint_core_elements: null,
      remediation_content: null,
      remediation_question: null,
      remediation_answer: null,
    }));

    return NextResponse.json(fallbackChunks);
  }

  return NextResponse.json(data);
}
