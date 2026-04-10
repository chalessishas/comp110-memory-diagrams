import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import type { ParsedOutlineNode } from "@/types";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: courseOwned } = await supabase.from("courses").select("id").eq("id", id).eq("user_id", user.id).single();
  if (!courseOwned) return NextResponse.json({ error: "Not found" }, { status: 404 });

  const { data, error } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", id)
    .order("order");

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  return NextResponse.json(data);
}

function flattenNodes(
  nodes: ParsedOutlineNode[],
  courseId: string,
  parentId: string | null = null
): { id: string; course_id: string; parent_id: string | null; title: string; type: string; content: string | null; order: number }[] {
  const rows: ReturnType<typeof flattenNodes> = [];
  nodes.forEach((node, index) => {
    const id = randomUUID();
    rows.push({
      id,
      course_id: courseId,
      parent_id: parentId,
      title: node.title,
      type: node.type,
      content: node.content ?? null,
      order: index,
    });
    if (node.children?.length) {
      rows.push(...flattenNodes(node.children, courseId, id));
    }
  });
  return rows;
}

export async function PUT(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { nodes, version } = await request.json();

  // Always verify course ownership before mutating
  const { data: course } = await supabase
    .from("courses")
    .select("updated_at")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();
  if (!course) return NextResponse.json({ error: "Not found" }, { status: 404 });

  // Optimistic locking: check updated_at matches what the client last saw
  if (version && course.updated_at !== version) {
    return NextResponse.json(
      { error: "Course was modified by another session. Please refresh." },
      { status: 409 }
    );
  }

  const rows = flattenNodes(nodes, id);

  // Atomic delete+insert via RPC (SECURITY INVOKER — respects RLS)
  const { data: count, error: rpcError } = await supabase.rpc("upsert_outline_nodes", {
    p_course_id: id,
    p_nodes: rows,
  });

  if (rpcError) return NextResponse.json({ error: rpcError.message }, { status: 500 });

  return NextResponse.json({ count: count ?? rows.length });
}
