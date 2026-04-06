import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data, error } = await supabase
    .from("exam_dates")
    .select("*")
    .eq("course_id", id)
    .order("exam_date");
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { title, exam_date, knowledge_point_ids } = await request.json();
  if (!title || !exam_date) return NextResponse.json({ error: "title and exam_date required" }, { status: 400 });

  const { data, error } = await supabase
    .from("exam_dates")
    .insert({ course_id: id, title, exam_date, knowledge_point_ids: knowledge_point_ids ?? [] })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data, { status: 201 });
}

export async function DELETE(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { exam_id } = await request.json();
  await supabase.from("exam_dates").delete().eq("id", exam_id);
  return NextResponse.json({ success: true });
}
