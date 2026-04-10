import { createClient } from "@/lib/supabase/server";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { stripThinkBlocks } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const model = qwen("qwen3.5-plus");

// POST: parse exam scope text → match to knowledge point IDs
// Returns matched KP IDs so the client can store them and filter all views
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  if (!await checkRateLimit(`exam-scope:${user.id}`, 5, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded. Try again in a minute." }, { status: 429 });
  }

  const { scope_text } = await request.json();
  if (!scope_text || typeof scope_text !== "string") {
    return NextResponse.json({ error: "scope_text required" }, { status: 400 });
  }

  // Fetch all knowledge points for this course
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title, content")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpList = kps ?? [];
  if (kpList.length === 0) {
    return NextResponse.json({ error: "No knowledge points found" }, { status: 400 });
  }

  const kpSummary = kpList.map((kp, i) => `${i + 1}. ${kp.title}`).join("\n");

  // AI matches scope text to existing knowledge points
  const { text } = await generateText({
    model,
    timeout: 55_000,
    messages: [{
      role: "user",
      content: `You are matching an exam scope description to a course's knowledge points.

Exam scope:
"""
${scope_text.slice(0, 3000)}
"""

Course knowledge points:
${kpSummary}

Return a JSON array of the NUMBERS (1-indexed) of knowledge points that fall within the exam scope.
Include a knowledge point if ANY part of it is likely to appear on the exam.
Be inclusive — if unsure, include it.

Return ONLY a JSON array like [1, 3, 5, 7]. No other text.`,
    }],
  });

  let matchedIndices: number[];
  try {
    const cleaned = stripThinkBlocks(text);
    const match = cleaned.match(/\[[\s\S]*?\]/);
    matchedIndices = match ? JSON.parse(match[0]) : [];
  } catch {
    return NextResponse.json({ error: "Failed to parse AI response" }, { status: 500 });
  }

  // Convert 1-indexed numbers to KP IDs
  const matchedKpIds = matchedIndices
    .filter((i) => i >= 1 && i <= kpList.length)
    .map((i) => kpList[i - 1].id);

  const matchedKpTitles = matchedIndices
    .filter((i) => i >= 1 && i <= kpList.length)
    .map((i) => kpList[i - 1].title);

  return NextResponse.json({
    matched_kp_ids: matchedKpIds,
    matched_kp_titles: matchedKpTitles,
    total_kps: kpList.length,
    matched_count: matchedKpIds.length,
  });
}

// GET: return knowledge points for this course (for manual selection)
export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", id)
    .eq("type", "knowledge_point")
    .order("created_at");

  return NextResponse.json(kps ?? []);
}
