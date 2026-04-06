import { createClient } from "@/lib/supabase/server";
import { generateLesson } from "@/lib/ai";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data, error } = await supabase
    .from("lessons")
    .select("*")
    .eq("course_id", id)
    .order("order");

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

// Generate lessons for all knowledge points that don't have one yet
export async function POST(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: course } = await supabase.from("courses").select("title, description").eq("id", id).single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  // Get knowledge points
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title, content")
    .eq("course_id", id)
    .eq("type", "knowledge_point")
    .order("order");

  if (!kps || kps.length === 0) {
    return NextResponse.json({ error: "No knowledge points found" }, { status: 400 });
  }

  // Check which already have lessons
  const { data: existing } = await supabase
    .from("lessons")
    .select("knowledge_point_id")
    .eq("course_id", id);

  const existingKpIds = new Set((existing ?? []).map((l) => l.knowledge_point_id));
  const missing = kps.filter((kp) => !existingKpIds.has(kp.id));

  if (missing.length === 0) {
    return NextResponse.json({ message: "All lessons already generated", count: 0 });
  }

  // Generate lessons one by one (sequential to avoid rate limits)
  const lessons = [];
  for (let i = 0; i < missing.length; i++) {
    try {
      const lesson = await generateLesson(course.title, missing[i], course.description ?? "");
      lessons.push({
        course_id: id,
        knowledge_point_id: missing[i].id,
        title: lesson.title,
        content: lesson.content,
        key_takeaways: lesson.key_takeaways,
        examples: lesson.examples,
        order: i,
      });
    } catch {
      // Skip failed lessons, continue with rest
    }
  }

  if (lessons.length > 0) {
    await supabase.from("lessons").insert(lessons);
  }

  return NextResponse.json({ count: lessons.length, total: missing.length });
}
