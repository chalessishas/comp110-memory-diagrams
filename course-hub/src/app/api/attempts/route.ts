import { createClient } from "@/lib/supabase/server";
import { attemptCreateSchema } from "@/lib/schemas";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Rate limit: prevents flooding the attempts table to game adaptive difficulty sorting
  if (!await checkRateLimit(`attempts:${user.id}`, 60, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const body = await request.json();
  const parsed = attemptCreateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const { data: question } = await supabase
    .from("questions")
    .select("answer, type, explanation, stem, knowledge_point_id")
    .eq("id", parsed.data.question_id)
    .single();

  if (!question) return NextResponse.json({ error: "Question not found" }, { status: 404 });

  const ua = parsed.data.user_answer.trim().toLowerCase().replace(/[.,;:!?'"()]/g, "").replace(/\s+/g, " ");
  const ea = question.answer.trim().toLowerCase().replace(/[.,;:!?'"()]/g, "").replace(/\s+/g, " ");

  let isCorrect: boolean;
  if (question.type === "short_answer") {
    // Key-term overlap: correct if ≥50% of meaningful answer words are present
    const userWords = new Set(ua.split(/\s+/));
    const answerWords = ea.split(/\s+/).filter((w: string) => w.length > 3);
    const matchCount = answerWords.filter((w: string) => userWords.has(w)).length;
    isCorrect = answerWords.length > 0 ? matchCount / answerWords.length >= 0.5 : ua.length > 0;
  } else if (question.type === "fill_blank") {
    // Fuzzy match: exact, contains, or numeric comparison
    if (ua === ea) { isCorrect = true; }
    else if (ua.includes(ea) || ea.includes(ua)) { isCorrect = true; }
    else {
      const uNum = parseFloat(ua), eNum = parseFloat(ea);
      isCorrect = !isNaN(uNum) && !isNaN(eNum) && Math.abs(uNum - eNum) < 0.001;
    }
  } else {
    isCorrect = ua === ea;
  }

  const { data, error } = await supabase
    .from("attempts")
    .insert({
      user_id: user.id,
      question_id: parsed.data.question_id,
      user_answer: parsed.data.user_answer,
      is_correct: isCorrect,
      confidence: parsed.data.confidence ?? null,
    })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // Keep mastery attempt counters current — required for exposed→practiced evaluation
  // Only updates existing rows (lesson completion creates the initial "exposed" record)
  if (question.knowledge_point_id) {
    const { data: mastery } = await supabase
      .from("element_mastery")
      .select("id, times_tested, times_correct")
      .eq("user_id", user.id)
      .eq("concept_id", question.knowledge_point_id)
      .maybeSingle();

    if (mastery) {
      await supabase
        .from("element_mastery")
        .update({
          times_tested: mastery.times_tested + 1,
          times_correct: mastery.times_correct + (isCorrect ? 1 : 0),
          updated_at: new Date().toISOString(),
        })
        .eq("id", mastery.id);
    }
  }

  // Track misconceptions: auto-log when user answers incorrectly for a knowledge point.
  // Increments occurrence_count on repeat; handles relapse if previously resolved.
  if (!isCorrect && question.knowledge_point_id) {
    const { data: existing } = await supabase
      .from("misconceptions")
      .select("id, occurrence_count, resolved, relapse_count")
      .eq("user_id", user.id)
      .eq("concept_id", question.knowledge_point_id)
      .maybeSingle();

    if (existing) {
      await supabase
        .from("misconceptions")
        .update({
          occurrence_count: existing.occurrence_count + 1,
          last_seen_at: new Date().toISOString(),
          ...(existing.resolved
            ? { resolved: false, relapsed: true, relapse_count: existing.relapse_count + 1 }
            : {}),
        })
        .eq("id", existing.id);
    } else {
      const desc = question.stem
        ? question.stem.slice(0, 120)
        : "Repeated errors on this topic";
      await supabase.from("misconceptions").insert({
        user_id: user.id,
        concept_id: question.knowledge_point_id,
        misconception_description: desc,
      });
    }
  }

  // Reveal answer + explanation only after submission
  return NextResponse.json({
    ...data,
    correct_answer: question.answer,
    explanation: question.explanation ?? null,
  }, { status: 201 });
}
