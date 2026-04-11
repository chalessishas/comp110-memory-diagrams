import { createClient } from "@/lib/supabase/server";
import { textModel, stripThinkBlocks } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";
import { generateText } from "ai";

export const maxDuration = 60;

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
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

  // Fetch question server-side — scoped to this course, answer never travels to client
  const { data: question } = await supabase
    .from("questions")
    .select("stem, answer, knowledge_point_id")
    .eq("id", question_id)
    .eq("course_id", id)
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

  // Persist result — required for mastery pathway (proficient → mastered needs has_teaching_challenge_pass)
  const kpId = question.knowledge_point_id;
  if (kpId) {
    // Log the challenge session
    await supabase.from("challenge_logs").insert({
      user_id: user.id,
      concept_id: kpId,
      session_type: "teaching_challenge",
      turns: [{ role: "user", content: user_explanation }],
      ai_confidence_rating: quality,
      final_confidence: quality === "strong" ? "solid" : quality === "partial" ? "partial" : "none",
    });

    // Unlock mastery gate on a strong explanation
    if (quality === "strong") {
      await supabase
        .from("element_mastery")
        .update({ has_teaching_challenge_pass: true, updated_at: new Date().toISOString() })
        .eq("user_id", user.id)
        .eq("concept_id", kpId)
        .eq("element_name", "_overall");
    }
  }

  return NextResponse.json({ feedback, quality });
}
