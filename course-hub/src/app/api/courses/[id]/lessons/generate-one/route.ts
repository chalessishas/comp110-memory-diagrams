import { createClient } from "@/lib/supabase/server";
import { generateLessonChunks, generateLessonOutline, generateSingleLessonChunk } from "@/lib/ai";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";

export const maxDuration = 60;

// Generate a lesson with interactive chunks for ONE knowledge point
// Supports ?stream=true for SSE progressive delivery (~5s to first chunk vs ~15s blocking)
export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });
  if (!await checkRateLimit(`gen-lesson:${user.id}`, 10, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded. Try again in a minute." }, { status: 429 });
  }

  const body = await request.json();
  const { knowledge_point_id, stream: wantStream } = body;
  if (!knowledge_point_id) return NextResponse.json({ error: "knowledge_point_id required" }, { status: 400 });

  // Check if lesson already exists
  const { data: existingLesson } = await supabase
    .from("lessons")
    .select("id")
    .eq("course_id", id)
    .eq("knowledge_point_id", knowledge_point_id)
    .limit(1)
    .single();

  if (existingLesson) {
    if (wantStream) {
      return sseResponse((send, close) => {
        send("done", { lesson_id: existingLesson.id, cached: true, chunks_generated: 0 });
        close();
      });
    }
    return NextResponse.json({ lesson_id: existingLesson.id, cached: true });
  }

  // Get course + knowledge point info
  const { data: course } = await supabase.from("courses").select("title, description").eq("id", id).eq("user_id", user.id).single();
  if (!course) return NextResponse.json({ error: "Course not found" }, { status: 404 });

  const { data: kp } = await supabase
    .from("outline_nodes")
    .select("title, content")
    .eq("id", knowledge_point_id)
    .single();

  if (!kp) return NextResponse.json({ error: "Knowledge point not found" }, { status: 404 });

  // ─── Streaming path: SSE with progressive chunk delivery ───
  if (wantStream) {
    return sseResponse(async (send, close) => {
      try {
        // Phase 1: outline (~2s)
        const outline = await generateLessonOutline(course.title, { title: kp.title, content: kp.content });
        send("outline", { total_chunks: outline.length, outline });

        // Create lesson record immediately so we have the ID
        const { data: lesson, error: lessonError } = await supabase
          .from("lessons")
          .insert({
            course_id: id,
            knowledge_point_id,
            title: kp.title,
            content: "", // will be filled after all chunks
            key_takeaways: outline.map(o => o.teaching_goal),
            examples: [],
            order: 0,
          })
          .select()
          .single();

        if (lessonError || !lesson) {
          send("error", { message: lessonError?.message ?? "Failed to create lesson" });
          close();
          return;
        }

        send("lesson", { lesson_id: lesson.id });

        // Phase 2: generate chunks in parallel, stream each as it completes
        let completedCount = 0;
        const allChunks: { chunk_index: number; content: string }[] = [];

        const chunkPromises = outline.map((_, index) =>
          generateSingleLessonChunk(course.title, outline, index).then(async (chunk) => {
            if (!chunk) return;

            // Insert into DB immediately
            await supabase.from("lesson_chunks").insert({
              lesson_id: lesson.id,
              chunk_index: chunk.chunk_index,
              content: chunk.content,
              checkpoint_type: chunk.checkpoint_type,
              checkpoint_prompt: chunk.checkpoint_prompt,
              checkpoint_answer: chunk.checkpoint_answer,
              checkpoint_options: chunk.checkpoint_options,
              key_terms: chunk.key_terms,
              widget_code: null, widget_description: null, widget_challenge: null,
              checkpoint_core_elements: null,
              remediation_content: null, remediation_question: null, remediation_answer: null,
            });

            allChunks.push({ chunk_index: chunk.chunk_index, content: chunk.content });
            completedCount++;

            // Stream chunk to client (without answer for security, same as questions API pattern)
            send("chunk", {
              chunk_index: chunk.chunk_index,
              content: chunk.content,
              checkpoint_type: chunk.checkpoint_type,
              checkpoint_prompt: chunk.checkpoint_prompt,
              checkpoint_options: chunk.checkpoint_options,
              key_terms: chunk.key_terms,
              // answer deliberately omitted — fetched via GET /chunks which includes it
            });
          })
        );

        await Promise.allSettled(chunkPromises);

        // Update lesson content with concatenated chunks
        const sortedContent = allChunks
          .sort((a, b) => a.chunk_index - b.chunk_index)
          .map(c => c.content)
          .join("\n\n---\n\n");

        await supabase.from("lessons").update({ content: sortedContent }).eq("id", lesson.id);

        send("done", { lesson_id: lesson.id, chunks_generated: completedCount });
      } catch (err) {
        send("error", { message: err instanceof Error ? err.message : "Generation failed" });
      }

      close();
    });
  }

  // ─── Blocking path (backward compatible) ───
  const { outline, chunks } = await generateLessonChunks(
    course.title,
    { title: kp.title, content: kp.content },
    course.description ?? "",
  );

  const { data: lesson, error: lessonError } = await supabase
    .from("lessons")
    .insert({
      course_id: id,
      knowledge_point_id,
      title: kp.title,
      content: chunks.map(c => c.content).join("\n\n---\n\n"),
      key_takeaways: outline.map(o => o.teaching_goal),
      examples: [],
      order: 0,
    })
    .select()
    .single();

  if (lessonError) return NextResponse.json({ error: lessonError.message }, { status: 500 });

  const chunkRows = chunks.map(c => ({
    lesson_id: lesson.id,
    chunk_index: c.chunk_index,
    content: c.content,
    checkpoint_type: c.checkpoint_type,
    checkpoint_prompt: c.checkpoint_prompt,
    checkpoint_answer: c.checkpoint_answer,
    checkpoint_options: c.checkpoint_options,
    key_terms: c.key_terms,
    widget_code: null, widget_description: null, widget_challenge: null,
    checkpoint_core_elements: null,
    remediation_content: null, remediation_question: null, remediation_answer: null,
  }));

  await supabase.from("lesson_chunks").insert(chunkRows);

  return NextResponse.json({
    lesson_id: lesson.id,
    chunks_generated: chunks.length,
    outline,
  });
}

// SSE helper: creates a ReadableStream that emits server-sent events
function sseResponse(handler: (
  send: (event: string, data: unknown) => void,
  close: () => void,
) => void | Promise<void>): Response {
  const encoder = new TextEncoder();

  const readable = new ReadableStream({
    async start(controller) {
      const send = (event: string, data: unknown) => {
        controller.enqueue(encoder.encode(`event: ${event}\ndata: ${JSON.stringify(data)}\n\n`));
      };
      const close = () => {
        try { controller.close(); } catch { /* already closed */ }
      };

      try {
        await handler(send, close);
      } catch (err) {
        send("error", { message: err instanceof Error ? err.message : "Unknown error" });
        close();
      }
    },
  });

  return new Response(readable, {
    headers: {
      "Content-Type": "text/event-stream",
      "Cache-Control": "no-cache, no-transform",
      Connection: "keep-alive",
      // Tells Vercel/Nginx proxy to flush chunks immediately, not buffer them
      "X-Accel-Buffering": "no",
    },
  });
}
