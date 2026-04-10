import { createClient } from "@/lib/supabase/server";
import { generateQuestionsFromOutline } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

const MAX_KPS_PER_CALL = 5;

export async function POST(_: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  if (!await checkRateLimit(`gen-questions:${user.id}`, 5, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded. Try again in a minute." }, { status: 429 });
  }

  const { data: course } = await supabase.from("courses").select("title").eq("id", id).eq("user_id", user.id).single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  // Get knowledge points that don't already have auto-generated questions
  const { data: allNodes } = await supabase
    .from("outline_nodes")
    .select("id, title, content, type")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kps = allNodes ?? [];
  if (kps.length === 0) {
    return NextResponse.json({ error: "No knowledge points found" }, { status: 400 });
  }

  // Check which KPs already have auto-generated questions
  const { data: existingQs } = await supabase
    .from("questions")
    .select("knowledge_point_id")
    .eq("course_id", id)
    .is("source_upload_id", null);

  const coveredKpIds = new Set((existingQs ?? []).map((q) => q.knowledge_point_id));
  const uncoveredKps = kps.filter((kp) => !coveredKpIds.has(kp.id));

  if (uncoveredKps.length === 0) {
    return NextResponse.json({ message: "All knowledge points already have questions", generated: 0 });
  }

  // Take first batch
  const batch = uncoveredKps.slice(0, MAX_KPS_PER_CALL);
  const kpData = batch.map((kp) => ({ title: kp.title, content: kp.content }));

  let questions: Awaited<ReturnType<typeof generateQuestionsFromOutline>> = [];
  try {
    questions = await generateQuestionsFromOutline(course.title, kpData);
  } catch (e) {
    return NextResponse.json({ error: e instanceof Error ? e.message : "Generation failed" }, { status: 500 });
  }

  const kpMap = new Map(batch.map((kp) => [kp.title.toLowerCase(), kp.id]));

  const rows = questions.map((q) => ({
    course_id: id,
    type: q.type,
    stem: q.stem,
    options: q.options,
    answer: q.answer,
    explanation: q.explanation,
    difficulty: q.difficulty,
    knowledge_point_id: kpMap.get(q.matched_kp_title.toLowerCase()) ?? null,
  }));

  if (rows.length > 0) {
    await supabase.from("questions").insert(rows);
  }

  return NextResponse.json({
    generated: rows.length,
    kps_covered: batch.length,
    kps_remaining: uncoveredKps.length - batch.length,
  });
}
