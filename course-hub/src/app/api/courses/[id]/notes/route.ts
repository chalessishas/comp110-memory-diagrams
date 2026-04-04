import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { noteCreateSchema } from "@/lib/schemas";

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: course } = await supabase
    .from("courses")
    .select("id")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();

  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  const body = await request.json();
  const parsed = noteCreateSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });
  }

  const { data, error } = await supabase
    .from("course_notes")
    .insert({
      course_id: id,
      ...parsed.data,
    })
    .select("*")
    .single();

  if (error) {
    const message = error.message.includes("course_notes")
      ? "The course_notes table is missing. Apply supabase/migrations/003_course_notes.sql first."
      : error.message;
    return NextResponse.json({ error: message }, { status: 500 });
  }
  return NextResponse.json({ note: data }, { status: 201 });
}
