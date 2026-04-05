import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { generateText, Output } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod";

const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const extractionSchema = z.object({
  sections: z.array(z.object({
    title: z.string(),
    summary: z.string(),
    key_concepts: z.array(z.string()),
    formulas: z.array(z.string()).default([]),
    matched_knowledge_point: z.string().nullable().default(null),
  })),
});

export async function POST(request: Request, { params }: { params: Promise<{ id: string }> }) {
  const { id } = await params;
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  const { storagePath } = await request.json();
  if (!storagePath) return NextResponse.json({ error: "storagePath required" }, { status: 400 });

  // Download file
  const { data: fileData } = await supabase.storage.from("course-files").download(storagePath);
  if (!fileData) return NextResponse.json({ error: "File not found" }, { status: 404 });

  const buffer = Buffer.from(await fileData.arrayBuffer());
  const base64 = buffer.toString("base64");
  const ext = storagePath.split(".").pop()?.toLowerCase() ?? "";
  const mimeType = ext === "pdf" ? "application/pdf" : `image/${ext}`;

  // Get knowledge points for matching
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpList = (kps ?? []).map((kp) => kp.title).join(", ");

  const { output } = await generateText({
    model: qwen("qwen-plus-latest"),
    messages: [{
      role: "user",
      content: [
        { type: "file", data: `data:${mimeType};base64,${base64}`, mediaType: mimeType as "application/pdf" },
        { type: "text", text: `Extract the key content from this document. For each section/chapter found, provide:
- title: section/chapter name
- summary: 2-3 sentence summary
- key_concepts: list of important terms and concepts
- formulas: any mathematical formulas or equations (empty array if none)
- matched_knowledge_point: which of these course knowledge points it relates to: [${kpList}]. Use null if no match.

Focus on educational value — what would a student need to know for an exam?` },
      ],
    }],
    output: Output.object({ schema: extractionSchema }),
  });

  const result = output as z.infer<typeof extractionSchema>;

  // Save extraction results to the upload record
  // Use exact file_name match to avoid ilike injection via user-controlled storagePath
  const fileName = storagePath.split("/").pop() ?? "";
  if (fileName) {
    await supabase
      .from("uploads")
      .update({ parsed_content: result, status: "done" })
      .eq("course_id", id)
      .eq("file_name", fileName);
  }

  return NextResponse.json(result);
}
