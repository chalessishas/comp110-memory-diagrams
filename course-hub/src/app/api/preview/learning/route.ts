import { createClient } from "@/lib/supabase/server";
import { generateStudyTasks, generateQuestionsFromOutline } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";
import type { ParsedOutlineNode } from "@/types";

export const maxDuration = 60;

function collectStudyTargets(nodes: ParsedOutlineNode[]) {
  const knowledgePoints: { title: string; content: string | null }[] = [];
  const leafNodes: { title: string; content: string | null }[] = [];

  function walk(items: ParsedOutlineNode[]) {
    for (const node of items) {
      if (node.type === "knowledge_point") {
        knowledgePoints.push({ title: node.title, content: node.content ?? null });
      }

      if (!node.children?.length) {
        leafNodes.push({ title: node.title, content: node.content ?? null });
      } else {
        walk(node.children);
      }
    }
  }

  walk(nodes);

  const source = knowledgePoints.length > 0 ? knowledgePoints : leafNodes;
  const seen = new Set<string>();

  return source.filter((item) => {
    const key = item.title.trim().toLowerCase();
    if (!key || seen.has(key)) return false;
    seen.add(key);
    return true;
  });
}

export async function POST(request: Request) {
  // Guest preview requires auth — unauthenticated AI calls burn API budget
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Sign in to preview AI-generated content" }, { status: 401 });

  const ip = request.headers.get("x-forwarded-for") ?? user.id;
  if (!checkRateLimit(ip, 10, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded. Try again in a minute." }, { status: 429 });
  }

  const { title, nodes } = await request.json();

  if (!title || !Array.isArray(nodes)) {
    return NextResponse.json({ error: "title and nodes required" }, { status: 400 });
  }

  const studyTargets = collectStudyTargets(nodes as ParsedOutlineNode[]);

  if (studyTargets.length === 0) {
    return NextResponse.json({ tasks: [], questions: [] });
  }

  const [tasks, questions] = await Promise.all([
    generateStudyTasks(title, studyTargets),
    generateQuestionsFromOutline(title, studyTargets),
  ]);

  return NextResponse.json({
    tasks,
    questions,
    study_targets_used: studyTargets.length,
  });
}
