import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { course_id, parent_id, title, type, content } = await request.json();
  if (!course_id || !title || !type) {
    return NextResponse.json({ error: "course_id, title, type required" }, { status: 400 });
  }

  // Get max order for siblings
  const { data: siblings } = await supabase
    .from("outline_nodes")
    .select("order")
    .eq("course_id", course_id)
    .is("parent_id", parent_id ?? null)
    .order("order", { ascending: false })
    .limit(1);

  const nextOrder = (siblings?.[0]?.order ?? -1) + 1;

  const { data, error } = await supabase
    .from("outline_nodes")
    .insert({ course_id, parent_id: parent_id ?? null, title, type, content: content ?? null, order: nextOrder })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data, { status: 201 });
}
