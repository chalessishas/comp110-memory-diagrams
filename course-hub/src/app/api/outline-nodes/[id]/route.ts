import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

async function verifyNodeOwnership(supabase: Awaited<ReturnType<typeof createClient>>, nodeId: string, userId: string): Promise<boolean> {
  const { data: node } = await supabase
    .from("outline_nodes")
    .select("course_id")
    .eq("id", nodeId)
    .single();
  if (!node) return false;

  const { data: course } = await supabase
    .from("courses")
    .select("id")
    .eq("id", node.course_id)
    .eq("user_id", userId)
    .single();
  return !!course;
}

export async function PATCH(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (!await verifyNodeOwnership(supabase, id, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  const body = await request.json();
  const allowed = ["title", "content", "type", "parent_id", "order"];
  const updates: Record<string, unknown> = {};
  for (const key of allowed) {
    if (key in body) updates[key] = body[key];
  }

  if (Object.keys(updates).length === 0) {
    return NextResponse.json({ error: "No valid fields to update" }, { status: 400 });
  }

  const { data, error } = await supabase
    .from("outline_nodes")
    .update(updates)
    .eq("id", id)
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

export async function DELETE(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (!await verifyNodeOwnership(supabase, id, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // CASCADE will delete children automatically (DB constraint)
  const { error } = await supabase.from("outline_nodes").delete().eq("id", id);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json({ success: true });
}
