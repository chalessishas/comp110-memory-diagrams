import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function POST(
  request: Request,
  { params }: { params: Promise<{ id: string; lessonId: string }> }
) {
  const { id: courseId, lessonId } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const { completed, lastChunkIndex, checkpointResults } = body;

  // Verify lesson belongs to this course and user owns it
  const { data: lesson } = await supabase
    .from("lessons")
    .select("id, knowledge_point_id, course_id")
    .eq("id", lessonId)
    .eq("course_id", courseId)
    .single();

  if (!lesson) return NextResponse.json({ error: "Lesson not found" }, { status: 404 });

  // Upsert lesson_progress
  const { error: progressError } = await supabase
    .from("lesson_progress")
    .upsert({
      user_id: user.id,
      lesson_id: lessonId,
      last_chunk_index: lastChunkIndex ?? 0,
      completed: completed ?? false,
      checkpoint_results: checkpointResults ?? {},
      ...(completed ? { completed_at: new Date().toISOString() } : {}),
    }, { onConflict: "user_id,lesson_id" });

  if (progressError) {
    return NextResponse.json({ error: progressError.message }, { status: 500 });
  }

  // If completed, bump mastery from "unseen" to "exposed" (first contact)
  if (completed && lesson.knowledge_point_id) {
    const { data: existing } = await supabase
      .from("element_mastery")
      .select("id, current_level")
      .eq("user_id", user.id)
      .eq("concept_id", lesson.knowledge_point_id)
      .eq("element_name", "_overall")
      .single();

    if (!existing) {
      // First time — create "exposed" mastery record
      await supabase.from("element_mastery").insert({
        user_id: user.id,
        concept_id: lesson.knowledge_point_id,
        element_name: "_overall",
        current_level: "exposed",
        first_contact_at: new Date().toISOString(),
      });
    } else if (existing.current_level === "unseen") {
      // Was unseen, now exposed
      await supabase
        .from("element_mastery")
        .update({ current_level: "exposed", level_reached_at: new Date().toISOString() })
        .eq("id", existing.id);
    }
    // If already exposed/practiced/proficient/mastered — don't downgrade
  }

  return NextResponse.json({ ok: true });
}
