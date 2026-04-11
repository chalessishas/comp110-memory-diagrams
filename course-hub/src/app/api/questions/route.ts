import { createClient } from "@/lib/supabase/server";
import { verifyCourseOwnership } from "@/lib/supabase/ownership";
import { parseExamQuestions } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const courseId = searchParams.get("courseId");
  if (!courseId) return NextResponse.json({ error: "courseId required" }, { status: 400 });

  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Verify course ownership before returning questions
  if (!await verifyCourseOwnership(supabase, courseId, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // Never send answer/explanation to client — revealed only after attempt submission
  const { data, error } = await supabase
    .from("questions")
    .select("id, course_id, source_upload_id, knowledge_point_id, type, stem, options, difficulty, created_at")
    .eq("course_id", courseId)
    .order("created_at", { ascending: false });

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  const questions = data ?? [];

  // Fetch this user's attempt stats per question for adaptive difficulty sorting
  const { data: attemptStats } = questions.length > 0
    ? await supabase
        .from("attempts")
        .select("question_id, is_correct")
        .eq("user_id", user.id)
        .in("question_id", questions.map((q) => q.id))
    : { data: [] };

  // Aggregate: count total and correct per question
  const statsMap = new Map<string, { total: number; correct: number }>();
  for (const a of attemptStats ?? []) {
    const s = statsMap.get(a.question_id) ?? { total: 0, correct: 0 };
    s.total++;
    if (a.is_correct) s.correct++;
    statsMap.set(a.question_id, s);
  }

  // Attach accuracy to each question
  const withStats = questions.map((q) => {
    const s = statsMap.get(q.id);
    return {
      ...q,
      attempt_count: s?.total ?? 0,
      user_accuracy: s ? s.correct / s.total : null,
    };
  });

  // Adaptive 85%-rule sort (Wilson et al. 2019, Nature Communications):
  // Target error rate ≈15% → optimal accuracy ≈0.85.
  // Priority 0 = show first.
  //   unseen (null)      → priority 1: introduce new material early
  //   accuracy 0.5–0.9   → priority 0: "desirable difficulty" sweet spot — most practice here
  //   accuracy < 0.5     → priority 2: struggling; include but don't overwhelm
  //   accuracy ≥ 0.9     → priority 3: near-mastered; show last
  // Within each band, shuffle for interleaving (Rohrer et al., g=0.42).
  const band = (acc: number | null): number => {
    if (acc === null) return 1;
    if (acc >= 0.5 && acc < 0.9) return 0;
    if (acc < 0.5) return 2;
    return 3;
  };
  const sorted = withStats
    .map((q) => ({ q, band: band(q.user_accuracy), jitter: Math.random() }))
    .sort((a, b) => a.band - b.band || a.jitter - b.jitter)
    .map(({ q }) => q);

  return NextResponse.json(sorted);
}

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const allowed = await checkRateLimit(`questions:extract:${user.id}`, 10, 60_000);
  if (!allowed) return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });

  const { courseId, storagePath } = await request.json();
  if (!courseId || !storagePath) {
    return NextResponse.json({ error: "courseId and storagePath required" }, { status: 400 });
  }

  if (!await verifyCourseOwnership(supabase, courseId, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // Verify file belongs to this course
  const { data: uploadRecord } = await supabase.from("uploads").select("id").eq("course_id", courseId).like("file_url", `%${storagePath}`).single();
  if (!uploadRecord) return NextResponse.json({ error: "File not found" }, { status: 404 });

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
