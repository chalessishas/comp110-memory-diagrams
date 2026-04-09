import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";

// Anomaly detection: flag questions that are likely incorrect or problematic.
// Runs per-course. Checks two signals:
// 1. User feedback: ≥2 independent "wrong_answer" reports
// 2. Statistical anomaly: accuracy < 15% with ≥5 attempts (likely wrong answer key)

const MIN_WRONG_REPORTS = 2;
const MIN_ATTEMPTS_FOR_STATS = 5;
const ACCURACY_THRESHOLD = 0.15;

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { courseId } = await request.json();
  if (!courseId) return NextResponse.json({ error: "courseId required" }, { status: 400 });

  // Verify user owns this course
  const { data: course } = await supabase
    .from("courses")
    .select("id")
    .eq("id", courseId)
    .eq("user_id", user.id)
    .single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  // 1. Find questions with ≥N "wrong_answer" feedback reports
  const { data: feedbackCounts } = await supabase
    .from("question_feedback")
    .select("question_id")
    .eq("reason", "wrong_answer");

  const feedbackByQuestion = new Map<string, number>();
  for (const fb of feedbackCounts ?? []) {
    feedbackByQuestion.set(fb.question_id, (feedbackByQuestion.get(fb.question_id) ?? 0) + 1);
  }

  // 2. Get all unflagged questions for this course
  const { data: questions } = await supabase
    .from("questions")
    .select("id")
    .eq("course_id", courseId)
    .eq("flagged", false);

  if (!questions || questions.length === 0) {
    return NextResponse.json({ checked: 0, flagged: 0 });
  }

  const questionIds = questions.map(q => q.id);

  // 3. Get attempt stats per question
  const { data: attempts } = await supabase
    .from("attempts")
    .select("question_id, is_correct")
    .in("question_id", questionIds);

  const attemptStats = new Map<string, { total: number; correct: number }>();
  for (const a of attempts ?? []) {
    const stats = attemptStats.get(a.question_id) ?? { total: 0, correct: 0 };
    stats.total++;
    if (a.is_correct) stats.correct++;
    attemptStats.set(a.question_id, stats);
  }

  // 4. Determine which questions to flag
  const toFlag: { id: string; reason: string }[] = [];

  for (const q of questions) {
    const reports = feedbackByQuestion.get(q.id) ?? 0;
    const stats = attemptStats.get(q.id);

    if (reports >= MIN_WRONG_REPORTS) {
      toFlag.push({ id: q.id, reason: `${reports} users reported wrong answer` });
      continue;
    }

    if (stats && stats.total >= MIN_ATTEMPTS_FOR_STATS) {
      const accuracy = stats.correct / stats.total;
      if (accuracy < ACCURACY_THRESHOLD) {
        toFlag.push({
          id: q.id,
          reason: `accuracy ${Math.round(accuracy * 100)}% (${stats.correct}/${stats.total}) below threshold`,
        });
      }
    }
  }

  // 5. Flag them
  const now = new Date().toISOString();
  for (const item of toFlag) {
    await supabase
      .from("questions")
      .update({ flagged: true, flagged_reason: item.reason, flagged_at: now })
      .eq("id", item.id);
  }

  return NextResponse.json({
    checked: questions.length,
    flagged: toFlag.length,
    details: toFlag,
  });
}
