import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";
import { noteOrganizeSchema } from "@/lib/schemas";
import { organizeStudyNote } from "@/lib/ai";
import type { OutlineNode } from "@/types";

function selectStudyTargets(nodes: OutlineNode[]) {
  const knowledgePoints = nodes.filter((node) => node.type === "knowledge_point");
  if (knowledgePoints.length > 0) return knowledgePoints;

  const parentIds = new Set(nodes.map((node) => node.parent_id).filter(Boolean));
  const leafNodes = nodes.filter((node) => !parentIds.has(node.id));
  if (leafNodes.length > 0) return leafNodes;

  return nodes;
}

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const parsed = noteOrganizeSchema.safeParse(body);
  if (!parsed.success) {
    return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });
  }

  const { data: course } = await supabase
    .from("courses")
    .select("id, title")
    .eq("id", id)
    .eq("user_id", user.id)
    .single();

  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  const { data: outlineNodes } = await supabase
    .from("outline_nodes")
    .select("id, parent_id, title, type, content, order, course_id")
    .eq("course_id", id)
    .order("order");

  const studyTargets = selectStudyTargets((outlineNodes ?? []) as OutlineNode[]);
  const targetMap = new Map(studyTargets.map((node) => [node.id, node]));
  const selectedKnowledgePoint = parsed.data.knowledge_point_id
    ? targetMap.get(parsed.data.knowledge_point_id) ?? null
    : null;

  const organized = await organizeStudyNote({
    courseTitle: course.title,
    transcript: parsed.data.transcript,
    knowledgePoints: studyTargets.map((node) => ({ title: node.title, content: node.content })),
    selectedKnowledgePointTitle: selectedKnowledgePoint?.title ?? null,
    clarificationAnswers: parsed.data.clarification_answers,
  });

  if (!organized.matched_knowledge_point_id && organized.matched_knowledge_point_title) {
    const matched = studyTargets.find(
      (node) => node.title.trim().toLowerCase() === organized.matched_knowledge_point_title?.trim().toLowerCase()
    );
    if (matched) {
      organized.matched_knowledge_point_id = matched.id;
      organized.matched_knowledge_point_title = matched.title;
    }
  }

  if (selectedKnowledgePoint) {
    organized.matched_knowledge_point_id = selectedKnowledgePoint.id;
    organized.matched_knowledge_point_title = selectedKnowledgePoint.title;
  }

  return NextResponse.json({ note: organized });
}
