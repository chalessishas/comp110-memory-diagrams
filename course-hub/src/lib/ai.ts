import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { parsedSyllabusSchema, parsedQuestionSchema } from "./schemas";
import { z } from "zod";
import type { OrganizedStudyNote, ParsedQuestion, ParsedSyllabus } from "@/types";

// Qwen3.5-Plus via DashScope OpenAI-compatible API
// $0.26/$1.56 per M tokens, native PDF vision, json_schema support
const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const visionModel = qwen("qwen-plus-latest");
const textModel = qwen("qwen-plus-latest");

const MAX_BASE64_SIZE = 20 * 1024 * 1024; // ~15MB decoded

// ─── Pipeline 1: Syllabus → Course Outline ───

export async function parseSyllabus(fileBase64: string, mimeType: string): Promise<ParsedSyllabus> {
  if (fileBase64.length > MAX_BASE64_SIZE) {
    throw new Error("File too large for AI processing (max ~15MB). Try a shorter document.");
  }

  try {
    const { text } = await generateText({
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

Organize by the document's natural structure. Break each section into specific knowledge points where possible.

Return ONLY valid JSON (no markdown, no code fences).`,
            },
          ],
        },
      ],
    });

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("AI did not return valid JSON");
    const parsed = parsedSyllabusSchema.parse(JSON.parse(jsonMatch[0]));
    return parsed as ParsedSyllabus;
  } catch (err) {
    throw new Error(`Syllabus parsing failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

export async function parseSyllabusText(rawText: string): Promise<ParsedSyllabus> {
  try {
    const { text } = await generateText({
      model: textModel,
      messages: [
        {
          role: "user",
          content: `Analyze the following course syllabus and extract its structure. Return ONLY valid JSON (no markdown, no code fences, no extra text). The JSON must have this exact shape:

{
  "title": "course name",
  "description": "one sentence description",
  "professor": "name or null",
  "semester": "e.g. Spring 2026 or null",
  "nodes": [
    {
      "title": "section title",
      "type": "week|chapter|topic|knowledge_point",
      "content": "brief description or null",
      "children": []
    }
  ]
}

Rules:
- "type" must be one of: "week", "chapter", "topic", "knowledge_point"
- Break each section into specific knowledge points where possible
- If the text is messy, infer the most likely course structure
- Return ONLY the JSON object, nothing else

Course text:
"""
${rawText}
"""`,
        },
      ],
    });

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("AI did not return valid JSON");

    const parsed = parsedSyllabusSchema.parse(JSON.parse(jsonMatch[0]));
    return parsed as ParsedSyllabus;
  } catch (err) {
    throw new Error(`Syllabus text parsing failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
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

  try {
    const { text } = await generateText({
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
- matched_kp_title: which of these knowledge points this question tests: [${kpList}]. Use null if no match.

Return ONLY valid JSON (no markdown, no code fences).`,
            },
          ],
        },
      ],
    });

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("AI did not return valid JSON");
    const parsed = questionsSchema.parse(JSON.parse(jsonMatch[0]));
    return parsed.questions;
  } catch (err) {
    throw new Error(`Exam question parsing failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
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

  try {
    const { text } = await generateText({
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

Focus on what a student actually needs to DO, not just what to know.

Return ONLY valid JSON (no markdown, no code fences).`,
        },
      ],
    });

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("AI did not return valid JSON");
    const parsed = studyTasksSchema.parse(JSON.parse(jsonMatch[0]));
    return parsed.tasks;
  } catch (err) {
    throw new Error(`Study task generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
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

  try {
    const { text } = await generateText({
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

Make questions test understanding, not just memorization.

Return ONLY valid JSON (no markdown, no code fences).`,
        },
      ],
    });

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("AI did not return valid JSON");
    const parsed = autoQuizSchema.parse(JSON.parse(jsonMatch[0]));
    return parsed.questions;
  } catch (err) {
    throw new Error(`Question generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

// ─── Pipeline 5: Spoken Study Notes → Structured Notes + Clarifying Questions ───

const organizedStudyNoteSchema = z.object({
  title: z.string().min(1),
  summary: z.string().min(1),
  key_points: z.array(z.string().min(1)).min(2).max(6),
  confusing_points: z.array(z.string().min(1)).max(4).default([]),
  next_action: z.string().nullable().default(null),
  clarification_questions: z.array(z.string().min(1)).max(3).default([]),
  matched_kp_title: z.string().nullable().default(null),
});

export async function organizeStudyNote({
  courseTitle,
  transcript,
  knowledgePoints,
  selectedKnowledgePointTitle,
  clarificationAnswers = [],
}: {
  courseTitle: string;
  transcript: string;
  knowledgePoints: { title: string; content: string | null }[];
  selectedKnowledgePointTitle?: string | null;
  clarificationAnswers?: string[];
}): Promise<OrganizedStudyNote> {
  const kpSummary = knowledgePoints.length
    ? knowledgePoints.map((kp) => `- ${kp.title}${kp.content ? `: ${kp.content}` : ""}`).join("\n")
    : "- No explicit knowledge points available";

  const clarificationContext = clarificationAnswers.filter(Boolean).length
    ? clarificationAnswers
        .filter(Boolean)
        .map((answer, index) => `Q${index + 1} answer: ${answer}`)
        .join("\n")
    : "No clarification answers yet.";

  try {
    const { text } = await generateText({
      model: textModel,
      messages: [
        {
          role: "user",
          content: `You are turning a student's spoken course note into a clean study note for the course "${courseTitle}".

Knowledge points in this course:
${kpSummary}

${selectedKnowledgePointTitle ? `The student manually tagged this note to: ${selectedKnowledgePointTitle}` : "No manual knowledge point tag was selected."}

Original spoken note:
"""
${transcript}
"""

Clarification answers so far:
${clarificationContext}

Return a structured note with:
- title: short and concrete
- summary: 2-4 sentences
- key_points: 2-6 bullet-sized takeaways
- confusing_points: only the parts the student still seems unsure about
- next_action: one concrete next step or null
- clarification_questions: 0-3 short follow-up questions only if the meaning is still ambiguous or incomplete
- matched_kp_title: exactly one title from the knowledge point list above, or null

Rules:
- Preserve the student's meaning. Do not invent facts.
- If a manual knowledge point was selected, use that as matched_kp_title.
- If the clarification answers already resolve the ambiguity, reduce or remove the clarification questions.
- If the note is clear enough, return an empty clarification_questions array.

Return ONLY valid JSON (no markdown, no code fences).`,
        },
      ],
    });

    const jsonMatch = text.match(/\{[\s\S]*\}/);
    if (!jsonMatch) throw new Error("AI did not return valid JSON");
    const organized = organizedStudyNoteSchema.parse(JSON.parse(jsonMatch[0]));

    return {
      title: organized.title,
      summary: organized.summary,
      key_points: organized.key_points,
      confusing_points: organized.confusing_points,
      next_action: organized.next_action,
      clarification_questions: organized.clarification_questions,
      matched_knowledge_point_id: null,
      matched_knowledge_point_title: selectedKnowledgePointTitle ?? organized.matched_kp_title,
    };
  } catch (err) {
    throw new Error(`Study note organization failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}
