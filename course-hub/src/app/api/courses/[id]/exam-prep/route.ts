import { createClient } from "@/lib/supabase/server";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { parsedQuestionSchema } from "@/lib/schemas";
import { NextResponse } from "next/server";

export const maxDuration = 60;

const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

// Exam Prep: paste exam scope text → generate targeted questions
// Generates 2 questions per topic, one topic at a time to avoid timeout
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { scope_text } = await request.json();
  if (!scope_text || typeof scope_text !== "string") {
    return NextResponse.json({ error: "scope_text required" }, { status: 400 });
  }

  // Step 1: Extract exam topics from the scope text (fast, small output)
  const { text: topicsText } = await generateText({
    model: qwen("qwen-plus-latest"),
    messages: [{
      role: "user",
      content: `Extract the exam topics from this text. Return a JSON array of strings, each being one specific testable topic. Be specific — "Alternating series test" not just "Series". Return ONLY a JSON array like ["topic1", "topic2"].

Text:
"""
${scope_text.slice(0, 3000)}
"""`
    }],
  });

  let topics: string[];
  try {
    const match = topicsText.match(/\[[\s\S]*\]/);
    topics = match ? JSON.parse(match[0]) : [];
  } catch {
    return NextResponse.json({ error: "Failed to extract topics" }, { status: 500 });
  }

  if (topics.length === 0) {
    return NextResponse.json({ error: "No topics found in the exam scope" }, { status: 400 });
  }

  // Step 2: Generate 2 questions per topic (sequential, one topic at a time)
  const allQuestions: { type: string; stem: string; options: unknown; answer: string; explanation: string | null; difficulty: number; topic: string }[] = [];

  for (const topic of topics.slice(0, 10)) { // max 10 topics
    try {
      const { text } = await generateText({
        model: qwen("qwen-plus-latest"),
        messages: [{
          role: "user",
          content: `Generate exactly 2 practice questions about "${topic}" for a Calculus II exam. Return JSON:
{"questions": [{"type": "multiple_choice", "stem": "...", "options": [{"label": "A", "text": "..."}, {"label": "B", "text": "..."}, {"label": "C", "text": "..."}, {"label": "D", "text": "..."}], "answer": "B", "explanation": "...", "difficulty": 3}]}

One should be multiple_choice, one should be fill_blank (options: null) or true_false (options: [{"label":"True","text":"True"},{"label":"False","text":"False"}]).
Questions should test the specific skills described in this topic. Return ONLY JSON.`
        }],
      });

      const match = text.match(/\{[\s\S]*\}/);
      if (match) {
        const raw = JSON.parse(match[0]);
        const qs = Array.isArray(raw) ? raw : (raw.questions ?? Object.values(raw).flat());
        for (const q of qs) {
          try {
            const parsed = parsedQuestionSchema.parse(q);
            allQuestions.push({ ...parsed, topic });
          } catch { /* skip malformed questions */ }
        }
      }
    } catch {
      // Skip topics that fail, continue with rest
    }
  }

  // Step 3: Insert all questions into DB
  if (allQuestions.length > 0) {
    // Try to match topics to existing knowledge points
    const { data: kps } = await supabase
      .from("outline_nodes")
      .select("id, title")
      .eq("course_id", id)
      .eq("type", "knowledge_point");

    const kpMap = new Map((kps ?? []).map((kp) => [kp.title.toLowerCase(), kp.id]));

    const rows = allQuestions.map((q) => ({
      course_id: id,
      type: q.type,
      stem: q.stem,
      options: q.options,
      answer: q.answer,
      explanation: q.explanation,
      difficulty: q.difficulty,
      knowledge_point_id: kpMap.get(q.topic.toLowerCase()) ?? null,
    }));

    await supabase.from("questions").insert(rows);
  }

  return NextResponse.json({
    topics_found: topics.length,
    questions_generated: allQuestions.length,
    topics,
  });
}
