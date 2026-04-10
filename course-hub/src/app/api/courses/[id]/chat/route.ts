import { createClient } from "@/lib/supabase/server";
import { streamText, convertToModelMessages, UIMessage } from "ai";
import { textModel } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 30;

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  if (!await checkRateLimit(`chat:${user.id}`, 20, 60_000)) {
    return NextResponse.json({ error: "Too many messages. Slow down." }, { status: 429 });
  }

  const { messages }: { messages: UIMessage[] } = await request.json();

  // Get course info + outline as context
  const { data: course } = await supabase
    .from("courses")
    .select("title, description, professor, semester")
    .eq("id", id)
    .single();

  const { data: nodes } = await supabase
    .from("outline_nodes")
    .select("title, type, content")
    .eq("course_id", id)
    .order("order");

  const outlineContext = (nodes ?? [])
    .map((n) => `[${n.type}] ${n.title}${n.content ? `: ${n.content}` : ""}`)
    .join("\n");

  const systemPrompt = `You are a helpful study assistant for the course "${course?.title || "Unknown"}".
Professor: ${course?.professor || "Unknown"}
Semester: ${course?.semester || "Unknown"}
Description: ${course?.description || ""}

Course outline and knowledge points:
${outlineContext}

Instructions:
- Answer questions based on the course content above
- If a question is outside the course scope, say so but still try to help
- Be concise and clear — students are studying, not reading essays
- Use examples when explaining concepts
- If you're not sure about something specific to this course, say so
- You can suggest which knowledge points to review for a topic`;

  const result = streamText({
    model: textModel,
    system: systemPrompt,
    messages: await convertToModelMessages(messages),
  });

  return result.toUIMessageStreamResponse();
}
