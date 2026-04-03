import { generateText, Output } from "ai";
import { openai } from "@ai-sdk/openai";
import { parsedSyllabusSchema, parsedQuestionSchema } from "./schemas";
import { z } from "zod";
import type { ParsedSyllabus, ParsedQuestion } from "@/types";

// GPT-4.1 nano: $0.10/$0.40 per M tokens (vs Claude Sonnet $3/$15)
const model = openai("gpt-4.1-nano");

export async function parseSyllabus(fileBase64: string, mimeType: string): Promise<ParsedSyllabus> {
  const { output } = await generateText({
    model,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "file",
            data: `data:${mimeType};base64,${fileBase64}`,
            mediaType: mimeType as "application/pdf",
          },
          {
            type: "text",
            text: `Analyze this course syllabus and extract its structure. Return:
- title: the course name
- description: a one-sentence course description
- professor: instructor name (null if not found)
- semester: semester info like "Fall 2026" (null if not found)
- nodes: hierarchical array of course content, where each node has:
  - title: section title
  - type: one of "week", "chapter", "topic", "knowledge_point"
  - content: brief description (null if obvious from title)
  - children: nested sub-sections

Organize by the document's natural structure. Break each section into specific knowledge points.`,
          },
        ],
      },
    ],
    output: Output.object({
      schema: parsedSyllabusSchema,
    }),
  });

  return output as ParsedSyllabus;
}

export async function parseExamQuestions(
  fileBase64: string,
  mimeType: string,
  knowledgePoints: { id: string; title: string }[]
): Promise<(ParsedQuestion & { matched_kp_title: string | null })[]> {
  const kpList = knowledgePoints.map((kp) => kp.title).join(", ");

  const questionsSchema = z.object({
    questions: parsedQuestionSchema
      .extend({ matched_kp_title: z.string().nullable().default(null) })
      .array(),
  });

  const { output } = await generateText({
    model,
    messages: [
      {
        role: "user",
        content: [
          {
            type: "file",
            data: `data:${mimeType};base64,${fileBase64}`,
            mediaType: mimeType as "application/pdf",
          },
          {
            type: "text",
            text: `Extract all questions from this exam/practice document. For each question return:
- type: "multiple_choice", "fill_blank", "short_answer", or "true_false"
- stem: the question text
- options: array of {label, text} for multiple choice (null otherwise)
- answer: the correct answer
- explanation: brief explanation of why this answer is correct
- difficulty: 1-5 (1=easy, 5=hard)
- matched_kp_title: which of these knowledge points this question tests: [${kpList}]. Use null if no match.`,
          },
        ],
      },
    ],
    output: Output.object({
      schema: questionsSchema,
    }),
  });

  return (output as z.infer<typeof questionsSchema>).questions;
}
