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

  let isCorrect: boolean;
  if (question.type === "short_answer") {
    // Key-term overlap: correct if ≥50% of meaningful answer words are present in user's answer
    const userWords = new Set(parsed.data.user_answer.trim().toLowerCase().split(/\s+/));
    const answerWords = question.answer.trim().toLowerCase().split(/\s+/).filter((w: string) => w.length > 3);
    const matchCount = answerWords.filter((w: string) => userWords.has(w)).length;
    isCorrect = answerWords.length > 0 ? matchCount / answerWords.length >= 0.5 : true;
  } else {
    isCorrect = parsed.data.user_answer.trim().toLowerCase() === question.answer.trim().toLowerCase();
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
