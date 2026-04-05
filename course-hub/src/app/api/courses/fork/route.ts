import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { randomUUID } from "crypto";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { token } = await request.json();
  if (!token) return NextResponse.json({ error: "token required" }, { status: 400 });

  // Find the shared course
  const { data: share } = await supabase
    .from("share_tokens")
    .select("course_id")
    .eq("token", token)
    .single();

  if (!share) return NextResponse.json({ error: "Invalid or expired link" }, { status: 404 });

  // Get original course
  const { data: original } = await supabase
    .from("courses")
    .select("title, description, professor, semester")
    .eq("id", share.course_id)
    .single();

  if (!original) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  // Create copy for current user
  const { data: newCourse, error: courseError } = await supabase
    .from("courses")
    .insert({
      user_id: user.id,
      title: `${original.title} (shared)`,
      description: original.description,
      professor: original.professor,
      semester: original.semester,
    })
    .select()
    .single();

  if (courseError) return NextResponse.json({ error: courseError.message }, { status: 500 });

  // Copy outline nodes
  const { data: originalNodes } = await supabase
    .from("outline_nodes")
    .select("*")
    .eq("course_id", share.course_id)
    .order("order");

  if (originalNodes && originalNodes.length > 0) {
    // Build ID mapping (old → new) to preserve parent_id relationships
    const idMap = new Map<string, string>();
    for (const node of originalNodes) {
      idMap.set(node.id, randomUUID());
    }

    const newNodes = originalNodes.map((node) => ({
      id: idMap.get(node.id)!,
      course_id: newCourse.id,
      parent_id: node.parent_id ? idMap.get(node.parent_id) ?? null : null,
      title: node.title,
      type: node.type,
      content: node.content,
      order: node.order,
    }));

    const { error: nodesError } = await supabase.from("outline_nodes").insert(newNodes);
    if (nodesError) {
      await supabase.from("courses").delete().eq("id", newCourse.id);
      return NextResponse.json({ error: "Failed to copy outline" }, { status: 500 });
    }
  }

  return NextResponse.json({ course_id: newCourse.id });
}
