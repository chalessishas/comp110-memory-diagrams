import { createClient } from "@/lib/supabase/server";
import { textModel, stripThinkBlocks } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";
import { generateText } from "ai";

export const maxDuration = 60;

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  await params; // ensure dynamic context
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (!await checkRateLimit(`teach-back:${user.id}`, 10, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const { question_id, user_explanation } = await request.json();
  if (!question_id || !user_explanation?.trim()) {
    return NextResponse.json({ error: "Missing fields" }, { status: 400 });
  }

  // Fetch question server-side — answer never travels to client
  const { data: question } = await supabase
    .from("questions")
    .select("stem, answer")
    .eq("id", question_id)
    .single();

  if (!question) return NextResponse.json({ error: "Question not found" }, { status: 404 });

  const { text } = await generateText({
    model: textModel,
    timeout: 30_000,
    messages: [{
      role: "user",
      content: `You are a tutor giving brief feedback on a student's explanation.

Question: ${question.stem}
Correct answer: ${question.answer}
Student's explanation: ${user_explanation}

In 2-3 sentences: acknowledge what they got right, point out any missing or incorrect concepts. Be encouraging but precise.
End your response with exactly one of these lines:
QUALITY: STRONG
QUALITY: PARTIAL
QUALITY: MISSING`,
    }],
  });

  const clean = stripThinkBlocks(text).trim();
  const qualityMatch = clean.match(/QUALITY:\s*(STRONG|PARTIAL|MISSING)/i);
  const quality = (qualityMatch?.[1]?.toLowerCase() ?? "partial") as "strong" | "partial" | "missing";
  const feedback = clean.replace(/QUALITY:\s*(STRONG|PARTIAL|MISSING)\s*$/i, "").trim();

  return NextResponse.json({ feedback, quality });
}
