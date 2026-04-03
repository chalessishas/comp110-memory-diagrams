import Anthropic from "@anthropic-ai/sdk";
import { parsedSyllabusSchema, parsedQuestionSchema } from "./schemas";
import type { ParsedSyllabus, ParsedQuestion } from "@/types";

const anthropic = new Anthropic({ apiKey: process.env.ANTHROPIC_API_KEY! });

export async function parseSyllabus(fileBase64: string, mimeType: string): Promise<ParsedSyllabus> {
  const response = await anthropic.messages.create({
    model: "claude-sonnet-4-5-20250514",
    max_tokens: 4096,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: { type: "base64", media_type: mimeType as "application/pdf", data: fileBase64 },
          },
          {
            type: "text",
            text: `Analyze this course syllabus and extract its structure. Return a JSON object with:
- title: the course name
- description: a one-sentence course description
- professor: instructor name (null if not found)
- semester: semester info like "Fall 2026" (null if not found)
- nodes: hierarchical array of course content, where each node has:
  - title: section title
  - type: one of "week", "chapter", "topic", "knowledge_point"
  - content: brief description of what this section covers (null if obvious from title)
  - children: nested sub-sections

Organize by the document's natural structure (weeks, chapters, units). Break each section into specific knowledge points where possible. Return ONLY valid JSON, no markdown.`,
          },
        ],
      },
    ],
  });

  const text = response.content.find((b) => b.type === "text")?.text ?? "";
  const jsonMatch = text.match(/\{[\s\S]*\}/);
  if (!jsonMatch) throw new Error("AI did not return valid JSON");

  const parsed = parsedSyllabusSchema.parse(JSON.parse(jsonMatch[0]));
  return parsed as ParsedSyllabus;
}

export async function parseExamQuestions(
  fileBase64: string,
  mimeType: string,
  knowledgePoints: { id: string; title: string }[]
): Promise<(ParsedQuestion & { matched_kp_title: string | null })[]> {
  const kpList = knowledgePoints.map((kp) => kp.title).join(", ");

  const response = await anthropic.messages.create({
    model: "claude-haiku-4-5-20251001",
    max_tokens: 8192,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "document",
            source: { type: "base64", media_type: mimeType as "application/pdf", data: fileBase64 },
          },
          {
            type: "text",
            text: `Extract all questions from this exam/practice document. For each question, return a JSON array where each item has:
- type: "multiple_choice", "fill_blank", "short_answer", or "true_false"
- stem: the question text
- options: array of {label, text} for multiple choice (null otherwise)
- answer: the correct answer
- explanation: brief explanation of why this answer is correct
- difficulty: 1-5 (1=easy, 5=hard)
- matched_kp_title: which of these knowledge points this question tests: [${kpList}]. Use null if no match.

Return ONLY a JSON array, no markdown.`,
          },
        ],
      },
    ],
  });

  const text = response.content.find((b) => b.type === "text")?.text ?? "";
  const jsonMatch = text.match(/\[[\s\S]*\]/);
  if (!jsonMatch) throw new Error("AI did not return valid JSON array");

  const questions = JSON.parse(jsonMatch[0]);
  return questions.map((q: unknown) => ({
    ...parsedQuestionSchema.parse(q),
    matched_kp_title: (q as Record<string, unknown>).matched_kp_title ?? null,
  }));
}
