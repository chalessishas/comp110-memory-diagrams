import { createClient } from "@/lib/supabase/server";
import { verifyCourseOwnership } from "@/lib/supabase/ownership";
import { NextResponse } from "next/server";

export interface MistakePattern {
  kp_id: string;
  kp_title: string;
  total_attempts: number;
  wrong_attempts: number;
  error_rate: number; // 0-1
  unique_questions: number;
  last_wrong_at: string | null;
}

// GET: return mistake patterns grouped by knowledge point, sorted by error rate desc
export async function GET(_request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (!await verifyCourseOwnership(supabase, id, user.id)) {
    return NextResponse.json({ error: "Not found" }, { status: 404 });
  }

  // Fetch questions with KP linkage
  const { data: questions } = await supabase
    .from("questions")
    .select("id, knowledge_point_id")
    .eq("course_id", id);

  if (!questions || questions.length === 0) {
    return NextResponse.json([]);
  }

  const questionIds = questions.map(q => q.id);

  // Fetch user's attempts
  const { data: attempts } = await supabase
    .from("attempts")
    .select("question_id, is_correct, answered_at")
    .eq("user_id", user.id)
    .in("question_id", questionIds);

  if (!attempts || attempts.length === 0) {
    return NextResponse.json([]);
  }

  // Fetch KP titles
  const kpIds = [...new Set(questions.map(q => q.knowledge_point_id).filter(Boolean))];
  const { data: kps } = kpIds.length > 0
    ? await supabase.from("outline_nodes").select("id, title").in("id", kpIds)
    : { data: [] };

  const kpMap = new Map((kps ?? []).map(k => [k.id, k.title]));

  // Build question → KP mapping
  const questionKpMap = new Map(questions.map(q => [q.id, q.knowledge_point_id]));

  // Aggregate by KP
  const stats = new Map<string, { total: number; wrong: number; questions: Set<string>; lastWrongAt: string | null }>();

  for (const a of attempts) {
    const kpId = questionKpMap.get(a.question_id);
    if (!kpId) continue;

    if (!stats.has(kpId)) {
      stats.set(kpId, { total: 0, wrong: 0, questions: new Set(), lastWrongAt: null });
    }
    const s = stats.get(kpId)!;
    s.total++;
    s.questions.add(a.question_id);
    if (!a.is_correct) {
      s.wrong++;
      if (!s.lastWrongAt || a.answered_at > s.lastWrongAt) {
        s.lastWrongAt = a.answered_at;
      }
    }
  }

  // Convert to sorted array
  const patterns: MistakePattern[] = [];
  for (const [kpId, s] of stats) {
    if (s.wrong === 0) continue; // only show KPs with mistakes
    patterns.push({
      kp_id: kpId,
      kp_title: kpMap.get(kpId) ?? "Unknown",
      total_attempts: s.total,
      wrong_attempts: s.wrong,
      error_rate: s.total > 0 ? s.wrong / s.total : 0,
      unique_questions: s.questions.size,
      last_wrong_at: s.lastWrongAt,
    });
  }

  patterns.sort((a, b) => b.error_rate - a.error_rate);

  return NextResponse.json(patterns);
}
