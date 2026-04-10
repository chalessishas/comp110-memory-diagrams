import { createClient } from "@/lib/supabase/server";
import { NextResponse } from "next/server";
import { generateText, Output } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { z } from "zod";

const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const sectionSchema = z.object({
  title: z.string().default("Untitled section"),
  summary: z.string().default(""),
  key_concepts: z.array(z.string()).default([]),
  formulas: z.array(z.string()).default([]),
  matched_knowledge_point: z.string().nullable().default(null),
});

// Accept both `{ sections: [...] }` and bare `[...]` — AI returns both shapes
const extractionSchema = z.union([
  z.object({ sections: z.array(sectionSchema).default([]) }),
  z.array(sectionSchema).transform((arr) => ({ sections: arr })),
]);

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
  const ext = storagePath.split(".").pop()?.toLowerCase() ?? "";

  // Get knowledge points for matching
  const { data: kps } = await supabase
    .from("outline_nodes")
    .select("id, title")
    .eq("course_id", id)
    .eq("type", "knowledge_point");

  const kpList = (kps ?? []).map((kp) => kp.title).join(", ");

  // Extract raw content from file.
  // - PDF: parse text server-side with pdf-parse (Qwen OpenAI-compat doesn't accept file type)
  // - Text/Markdown: use buffer directly
  // - Images: send as image_url to vision model (fallback, not implemented here)
  let documentText = "";
  if (ext === "pdf") {
    try {
      const { PDFParse } = await import("pdf-parse");
      // Point worker to the local pdfjs-dist legacy build so Next.js dev mode can resolve it
      PDFParse.setWorker(
        new URL("../../../../../../node_modules/pdfjs-dist/legacy/build/pdf.worker.mjs", import.meta.url).href,
      );
      const parser = new PDFParse({ data: new Uint8Array(buffer) });
      const textResult = await parser.getText();
      documentText = textResult.text;
      await parser.destroy();
    } catch (err) {
      return NextResponse.json(
        { error: `PDF parsing failed: ${err instanceof Error ? err.message : "unknown error"}` },
        { status: 400 },
      );
    }
  } else if (ext === "txt" || ext === "md" || ext === "markdown") {
    documentText = buffer.toString("utf-8");
  } else {
    return NextResponse.json(
      { error: `Unsupported file type: ${ext}. Supported: pdf, txt, md` },
      { status: 400 },
    );
  }

  if (!documentText.trim()) {
    return NextResponse.json({ error: "Document contains no extractable text" }, { status: 400 });
  }

  // Truncate to avoid token limit (Qwen supports ~32k but safer to cap)
  const truncated = documentText.slice(0, 20_000);

  const { output } = await generateText({
    model: qwen.chat("qwen3.5-plus"),
    messages: [{
      role: "user",
      content: `Extract the key content from this document and return JSON. For each section/chapter found, provide:
- title: section/chapter name
- summary: 2-3 sentence summary
- key_concepts: list of important terms and concepts
- formulas: any mathematical formulas or equations (empty array if none)
- matched_knowledge_point: which of these course knowledge points it relates to: [${kpList}]. Use null if no match.

Focus on educational value — what would a student need to know for an exam? Return structured JSON only.

Document content:
"""
${truncated}
"""`,
    }],
    output: Output.object({ schema: extractionSchema }),
  });

  const result = output as z.infer<typeof extractionSchema>;

  // Save extraction results to the upload record
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
