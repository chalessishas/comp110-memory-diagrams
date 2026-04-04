import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET() {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Get bookmarks with full question + course info
  const { data, error } = await supabase
    .from("question_bookmarks")
    .select(`
      id, note, created_at,
      questions:question_id (
        id, stem, type, options, answer, explanation, difficulty, course_id,
        courses:course_id ( title )
      )
    `)
    .eq("user_id", user.id)
    .order("created_at", { ascending: false });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { question_id, note } = await request.json();
  if (!question_id) return NextResponse.json({ error: "question_id required" }, { status: 400 });

  const { data, error } = await supabase
    .from("question_bookmarks")
    .upsert({ user_id: user.id, question_id, note: note ?? null }, { onConflict: "user_id,question_id" })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data, { status: 201 });
}

export async function DELETE(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { question_id } = await request.json();

  const { error } = await supabase
    .from("question_bookmarks")
    .delete()
    .eq("user_id", user.id)
    .eq("question_id", question_id);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ success: true });
}
