import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { randomUUID } from "crypto";
import type { ParsedOutlineNode } from "@/types";

export async function GET(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();

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
  const { nodes } = await request.json();

  await supabase.from("outline_nodes").delete().eq("course_id", id);

  const rows = flattenNodes(nodes, id);
  if (rows.length > 0) {
    const { error } = await supabase.from("outline_nodes").insert(rows);
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });
  }

  return NextResponse.json({ count: rows.length });
}
