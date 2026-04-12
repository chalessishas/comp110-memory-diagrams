import { createClient } from "@/lib/supabase/server";
import { verifyCourseOwnership } from "@/lib/supabase/ownership";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // 120/min — allows fast bulk outline creation; prevents KP spam
  if (!await checkRateLimit(`outline-nodes:${user.id}`, 120, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const { course_id, parent_id, title, type, content } = await request.json();
  if (!course_id || !title || !type) {
    return NextResponse.json({ error: "course_id, title, type required" }, { status: 400 });
  }

  if (!await verifyCourseOwnership(supabase, course_id, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // Verify parent_id (if provided) belongs to the same course — prevents cross-course orphaned nodes
  if (parent_id) {
    const { data: parentNode } = await supabase
      .from("outline_nodes")
      .select("id")
      .eq("id", parent_id)
      .eq("course_id", course_id)
      .single();
    if (!parentNode) return NextResponse.json({ error: "Not found" }, { status: 404 });
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
