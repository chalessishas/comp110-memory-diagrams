import { createClient } from "@/lib/supabase/server";
import { attemptCreateSchema } from "@/lib/schemas";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const body = await request.json();
  const parsed = attemptCreateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const { data: question } = await supabase
    .from("questions")
    .select("answer, type, explanation")
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
    })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // Reveal answer + explanation only after submission
  return NextResponse.json({
    ...data,
    correct_answer: question.answer,
    explanation: question.explanation ?? null,
  }, { status: 201 });
}
