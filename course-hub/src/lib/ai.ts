import { generateText, Output } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { parsedSyllabusSchema, parsedQuestionSchema } from "./schemas";
import { z } from "zod";
import type { ParsedSyllabus, ParsedQuestion } from "@/types";

// Qwen3.5-Plus via DashScope OpenAI-compatible API
// $0.26/$1.56 per M tokens, native PDF vision, json_schema support
const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const visionModel = qwen("qwen-plus-latest");
const textModel = qwen("qwen-plus-latest");

// ─── Pipeline 1: Syllabus → Course Outline ───

export async function parseSyllabus(fileBase64: string, mimeType: string): Promise<ParsedSyllabus> {
  const { output } = await generateText({
    model: visionModel,
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

Organize by the document's natural structure. Break each section into specific knowledge points where possible.`,
          },
        ],
      },
    ],
    output: Output.object({ schema: parsedSyllabusSchema }),
  });

  return output as ParsedSyllabus;
}

// ─── Pipeline 2: Exam/Practice → Interactive Questions ───

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
    model: visionModel,
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
    output: Output.object({ schema: questionsSchema }),
  });

  return (output as z.infer<typeof questionsSchema>).questions;
}

// ─── Pipeline 3: Outline → Study Tasks (auto-generated) ───

export interface StudyTask {
  knowledge_point_title: string;
  title: string;
  description: string;
  task_type: "read" | "practice" | "review";
  priority: number; // 1=high, 3=low
}

const studyTasksSchema = z.object({
  tasks: z.array(z.object({
    knowledge_point_title: z.string(),
    title: z.string(),
    description: z.string(),
    task_type: z.enum(["read", "practice", "review"]),
    priority: z.number().int().min(1).max(3),
  })),
});

export async function generateStudyTasks(
  courseTitle: string,
  knowledgePoints: { title: string; content: string | null }[]
): Promise<StudyTask[]> {
  const kpSummary = knowledgePoints
    .map((kp, i) => `${i + 1}. ${kp.title}${kp.content ? ` — ${kp.content}` : ""}`)
    .join("\n");

  const { output } = await generateText({
    model: textModel,
    messages: [
      {
        role: "user",
        content: `You are a study planner for the course "${courseTitle}".

Here are the knowledge points from the course outline:
${kpSummary}

For each knowledge point, generate 1-3 study tasks. Each task should be:
- Actionable and specific (not vague like "study chapter 3")
- Categorized as "read" (learn the concept), "practice" (do exercises), or "review" (revisit/summarize)
- Prioritized: 1=must-know (core concept), 2=should-know (important detail), 3=nice-to-know (supplementary)

Focus on what a student actually needs to DO, not just what to know.`,
      },
    ],
    output: Output.object({ schema: studyTasksSchema }),
  });

  return (output as z.infer<typeof studyTasksSchema>).tasks;
}

// ─── Pipeline 4: Outline → Auto Quiz Questions (no exam needed) ───

export async function generateQuestionsFromOutline(
  courseTitle: string,
  knowledgePoints: { title: string; content: string | null }[]
): Promise<(ParsedQuestion & { matched_kp_title: string })[]> {
  const kpSummary = knowledgePoints
    .map((kp) => `- ${kp.title}${kp.content ? `: ${kp.content}` : ""}`)
    .join("\n");

  const autoQuizSchema = z.object({
    questions: parsedQuestionSchema
      .extend({ matched_kp_title: z.string() })
      .array(),
  });

  const { output } = await generateText({
    model: textModel,
    messages: [
      {
        role: "user",
        content: `You are creating practice questions for the course "${courseTitle}".

Knowledge points:
${kpSummary}

Generate 2-3 practice questions per knowledge point. Mix question types:
- multiple_choice: 4 options (A/B/C/D), exactly one correct
- fill_blank: leave a key term blank for the student to fill
- true_false: 2 options [{label:"True",text:"True"},{label:"False",text:"False"}]
- short_answer: open-ended, 1-2 sentence answer expected

Each question must have:
- A clear, unambiguous stem
- A correct answer with explanation
- difficulty 1-5
- matched_kp_title: exactly matching one of the knowledge point titles listed above

Make questions test understanding, not just memorization.`,
      },
    ],
    output: Output.object({ schema: autoQuizSchema }),
  });

  return (output as z.infer<typeof autoQuizSchema>).questions;
}
