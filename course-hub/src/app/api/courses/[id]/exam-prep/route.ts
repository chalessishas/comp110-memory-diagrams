import { createClient } from "@/lib/supabase/server";
import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { parsedQuestionSchema } from "@/lib/schemas";
import { stripThinkBlocks } from "@/lib/ai";
import { NextResponse } from "next/server";

export const maxDuration = 60;

const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const model = qwen("qwen3.5-plus");

// Exam Prep: paste exam scope text → generate targeted questions
// qwen3.5-plus is fast enough to handle 10+ topics within 60s
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { scope_text } = await request.json();
  if (!scope_text || typeof scope_text !== "string") {
    return NextResponse.json({ error: "scope_text required" }, { status: 400 });
  }

  // Step 1: Extract exam topics from the scope text
  const { text: topicsText } = await generateText({
    model,
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
    const match = stripThinkBlocks(topicsText).match(/\[[\s\S]*\]/);
    topics = match ? JSON.parse(match[0]) : [];
  } catch {
    return NextResponse.json({ error: "Failed to extract topics" }, { status: 500 });
  }

  if (topics.length === 0) {
    return NextResponse.json({ error: "No topics found in the exam scope" }, { status: 400 });
  }

  // Step 2: Generate 2 questions per topic in parallel batches of 4
  type GenQ = { type: string; stem: string; options: unknown; answer: string; explanation: string | null; difficulty: number; topic: string };
  const allQuestions: GenQ[] = [];
  const topicsFailed: string[] = [];
  const maxTopics = Math.min(topics.length, 12);

  for (let i = 0; i < maxTopics; i += 4) {
    const batch = topics.slice(i, i + 4);
    const results = await Promise.allSettled(batch.map(async (topic) => {
      const { text } = await generateText({
        model,
        messages: [{
          role: "user",
          content: `Generate exactly 2 practice questions about "${topic}" for a Calculus II exam. Return JSON:
{"questions": [{"type": "multiple_choice", "stem": "...", "options": [{"label": "A", "text": "..."}, {"label": "B", "text": "..."}, {"label": "C", "text": "..."}, {"label": "D", "text": "..."}], "answer": "B", "explanation": "...", "difficulty": 3}]}

One should be multiple_choice, one should be fill_blank (options: null) or true_false (options: [{"label":"True","text":"True"},{"label":"False","text":"False"}]).
Questions should test the specific skills described in this topic. Return ONLY JSON.`
        }],
      });

      const match = stripThinkBlocks(text).match(/\{[\s\S]*\}/);
      if (!match) return { topic, questions: [] as GenQ[] };

      const raw = JSON.parse(match[0]);
      const qs = Array.isArray(raw) ? raw : (raw.questions ?? Object.values(raw).flat());
      const parsed: GenQ[] = [];
      for (const q of qs) {
        const r = parsedQuestionSchema.safeParse(q);
        if (r.success) parsed.push({ ...r.data, topic });
      }
      return { topic, questions: parsed };
    }));

    for (let j = 0; j < results.length; j++) {
      const r = results[j];
      if (r.status === "fulfilled" && r.value.questions.length > 0) {
        allQuestions.push(...r.value.questions);
      } else {
        topicsFailed.push(batch[j]);
      }
    }
  }

  // Step 3: Insert all questions with fuzzy KP matching
  if (allQuestions.length > 0) {
    const { data: kps } = await supabase
      .from("outline_nodes")
      .select("id, title")
      .eq("course_id", id)
      .eq("type", "knowledge_point");

    const kpList = kps ?? [];
    const kpMap = new Map(kpList.map((kp) => [kp.title.toLowerCase(), kp.id]));

    function findKpId(topic: string): string | null {
      const t = topic.toLowerCase();
      if (kpMap.has(t)) return kpMap.get(t)!;
      // Fuzzy: check if topic contains or is contained by any KP title
      for (const kp of kpList) {
        const kpLower = kp.title.toLowerCase();
        if (kpLower.includes(t) || t.includes(kpLower)) return kp.id;
      }
      return null;
    }

    const rows = allQuestions.map((q) => ({
      course_id: id,
      type: q.type,
      stem: q.stem,
      options: q.options,
      answer: q.answer,
      explanation: q.explanation,
      difficulty: q.difficulty,
      knowledge_point_id: findKpId(q.topic),
    }));

    await supabase.from("questions").insert(rows);
  }

  return NextResponse.json({
    topics_found: topics.length,
    topics_processed: maxTopics,
    questions_generated: allQuestions.length,
    topics_failed: topicsFailed,
    topics,
  });
}
