import { createClient } from "@/lib/supabase/server";
import { parseExamQuestions } from "@/lib/ai";
import { NextResponse } from "next/server";

export const maxDuration = 60;

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const courseId = searchParams.get("courseId");
  if (!courseId) return NextResponse.json({ error: "courseId required" }, { status: 400 });

  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Never send answer/explanation to client — revealed only after attempt submission
  // Exclude flagged questions (reported wrong / auto-detected anomalies)
  const { data, error } = await supabase
    .from("questions")
    .select("id, course_id, source_upload_id, knowledge_point_id, type, stem, options, difficulty, flagged, flagged_reason, created_at")
    .eq("course_id", courseId)
    .eq("flagged", false)
    .order("created_at", { ascending: false });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // Interleaved practice: shuffle questions so different knowledge points are mixed
  // Evidence: interleaving produces g=0.42 overall, d=1.05-1.21 in math (Rohrer et al.)
  const shuffled = [...(data ?? [])].sort(() => Math.random() - 0.5);
  return NextResponse.json(shuffled);
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { courseId, storagePath } = await request.json();
  if (!courseId || !storagePath) {
    return NextResponse.json({ error: "courseId and storagePath required" }, { status: 400 });
  }

  const { data: fileData } = await supabase.storage.from("course-files").download(storagePath);
  if (!fileData) return NextResponse.json({ error: "File not found" }, { status: 404 });

  const buffer = Buffer.from(await fileData.arrayBuffer());
  const base64 = buffer.toString("base64");
  const ext = storagePath.split(".").pop()?.toLowerCase() ?? "";
  const mimeType = ext === "pdf" ? "application/pdf" : `image/${ext}`;

  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", courseId)
    .eq("type", "knowledge_point");

  const parsed = await parseExamQuestions(base64, mimeType, kps ?? []);

  const kpMap = new Map((kps ?? []).map((kp) => [kp.title.toLowerCase(), kp.id]));

  const rows = parsed.map((q) => ({
    course_id: courseId,
    type: q.type,
    stem: q.stem,
    options: q.options,
    answer: q.answer,
    explanation: q.explanation,
    difficulty: q.difficulty,
    knowledge_point_id: q.matched_kp_title ? kpMap.get(q.matched_kp_title.toLowerCase()) ?? null : null,
  }));

  const { data: inserted, error } = await supabase.from("questions").insert(rows).select();
  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json(inserted, { status: 201 });
}
