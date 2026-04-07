import { generateText } from "ai";
import { createOpenAI } from "@ai-sdk/openai";
import { parsedSyllabusSchema, parsedQuestionSchema, generatedLessonSchema } from "./schemas";
import { z } from "zod";
import type { OrganizedStudyNote, ParsedQuestion, ParsedSyllabus } from "@/types";

// Qwen3.5-Plus via DashScope OpenAI-compatible API
// $0.26/$1.56 per M tokens, native PDF vision, json_schema support
const qwen = createOpenAI({
  baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
  apiKey: process.env.DASHSCOPE_API_KEY ?? "",
});

const visionModel = qwen("qwen-plus-latest"); // multimodal — PDF/image parsing (proven stable)
const textModel = qwen("qwen3.5-plus"); // 19x faster than qwen-plus (MoE, 17B active params)

const MAX_BASE64_SIZE = 20 * 1024 * 1024; // ~15MB decoded
// Temporarily disabled AbortSignal — investigating generate failures
const AI_TIMEOUT_MS = 55_000;

// Strip qwen3.5-plus thinking mode leaks (can corrupt JSON output)
export function stripThinkBlocks(text: string): string {
  return text.replace(/<think>[\s\S]*?<\/think>/g, "").trim();
}

// Fix #9: robust JSON extraction — strips markdown fences + think blocks, finds object or array
function extractJSON(text: string): string | null {
  // Strip qwen3.5-plus thinking mode leaks and markdown code fences
  const cleaned = text
    .replace(/<think>[\s\S]*?<\/think>/g, "")
    .replace(/```(?:json)?\s*/g, "")
    .replace(/```\s*/g, "");
  // Try to find JSON object
  const objMatch = cleaned.match(/\{[\s\S]*\}/);
  if (objMatch) return objMatch[0];
  // Try array
  const arrMatch = cleaned.match(/\[[\s\S]*\]/);
  if (arrMatch) return arrMatch[0];
  return null;
}

// ─── Pipeline 1: Syllabus → Course Outline ───

export async function parseSyllabus(fileBase64: string, mimeType: string, language?: string): Promise<ParsedSyllabus> {
  if (fileBase64.length > MAX_BASE64_SIZE) {
    throw new Error("File too large for AI processing (max ~15MB). Try a shorter document.");
  }

  const langInstruction = language ? `\n\nIMPORTANT: Generate ALL content in ${language === "zh" ? "Chinese (简体中文)" : "English"}. All titles, descriptions, explanations, and answers must be in ${language === "zh" ? "Chinese" : "English"}.` : "";

  try {
    const { text } = await generateText({
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
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
              text: `Analyze this course syllabus and extract its structure as a NESTED hierarchy.

Return JSON with: title, description, professor (null if not found), semester (null if not found), confidence ("high"/"medium"/"low"), missing_info (array), and nodes.

Each node: { title, type, content (null if obvious), children }
Types: "week", "chapter", "topic", "knowledge_point"

CRITICAL: Every week/chapter MUST have children. Sub-topics and bullet points become "knowledge_point" children. Do NOT create flat week nodes with empty children. Leaf nodes must be type "knowledge_point".

Return ONLY valid JSON (no markdown, no code fences).${langInstruction}`,
            },
          ],
        },
      ],
    });

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");
    const parsed = parsedSyllabusSchema.parse(JSON.parse(jsonStr));
    return parsed as ParsedSyllabus;
  } catch (err) {
    throw new Error(`Syllabus parsing failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

export async function parseSyllabusText(rawText: string, language?: string): Promise<ParsedSyllabus> {
  const langInstruction = language ? `\n\nIMPORTANT: Generate ALL content in ${language === "zh" ? "Chinese (简体中文)" : "English"}. All titles, descriptions, explanations, and answers must be in ${language === "zh" ? "Chinese" : "English"}.` : "";

  try {
    const { text } = await generateText({
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
      model: textModel,
      messages: [
        {
          role: "user",
          content: `You are analyzing a course syllabus to extract its ACTUAL teaching content as a nested hierarchy. Return ONLY valid JSON (no markdown, no code fences).

CRITICAL RULES:
1. Only extract topics/knowledge points that are EXPLICITLY mentioned. Do NOT invent topics.
2. Administrative content (grading, attendance, accommodations) is NOT course content.
3. EVERY week/chapter MUST have children. Sub-topics and bullet points from the syllabus become children with type "knowledge_point". If a week lists "Integration by parts, Partial fractions", those are TWO separate knowledge_point children.
4. The hierarchy should be: week/chapter → topic → knowledge_point. Use at least 2 levels. Leaf nodes should be type "knowledge_point".
5. If the syllabus lacks a detailed topic schedule, set confidence to "low".

JSON shape:
{
  "title": "course name",
  "description": "one sentence description",
  "professor": "name or null",
  "semester": "e.g. Spring 2026 or null",
  "confidence": "high|medium|low",
  "missing_info": [],
  "nodes": [
    {
      "title": "Week 1: Functions",
      "type": "week",
      "content": null,
      "children": [
        { "title": "Domain and range", "type": "knowledge_point", "content": "Determining domain and range of functions", "children": [] },
        { "title": "Composition of functions", "type": "knowledge_point", "content": null, "children": [] }
      ]
    }
  ]
}

IMPORTANT: Do NOT create flat week nodes with empty children. Every week/chapter that lists sub-topics MUST have those sub-topics as knowledge_point children.

Course text:
"""
${rawText}
"""${langInstruction}`,
        },
      ],
    });

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");

    const parsed = parsedSyllabusSchema.parse(JSON.parse(jsonStr));
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
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
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

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");
    const raw = JSON.parse(jsonStr);
    const wrapped = Array.isArray(raw) ? { questions: raw } : raw;
    const parsed = questionsSchema.parse(wrapped);
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

// Lenient studyTasksSchema — handles various AI output formats
const normalizeTaskType = (val: string) => {
  const v = val.toLowerCase().replace(/[-_\s]/g, "");
  if (v.includes("read") || v.includes("study") || v.includes("learn")) return "read" as const;
  if (v.includes("practice") || v.includes("exercise") || v.includes("drill") || v.includes("do")) return "practice" as const;
  if (v.includes("review") || v.includes("revisit") || v.includes("recap") || v.includes("summary")) return "review" as const;
  return "read" as const;
};

const studyTasksSchema = z.object({
  tasks: z.array(z.any().transform((item) => {
    const obj = item as Record<string, unknown>;
    return {
      knowledge_point_title: String(obj.knowledge_point_title ?? obj.knowledgePoint ?? obj.topic ?? ""),
      title: String(obj.title ?? obj.task ?? obj.name ?? "Study task"),
      description: String(obj.description ?? obj.task ?? obj.details ?? ""),
      task_type: normalizeTaskType(String(obj.task_type ?? obj.type ?? obj.category ?? "read")),
      priority: (() => {
        const n = typeof obj.priority === "string" ? parseInt(obj.priority, 10) : Number(obj.priority ?? 2);
        return isNaN(n) ? 2 : Math.max(1, Math.min(3, Math.round(n)));
      })(),
    };
  })),
});

export async function generateStudyTasks(
  courseTitle: string,
  knowledgePoints: { title: string; content: string | null }[],
  language?: string
): Promise<StudyTask[]> {
  const kpSummary = knowledgePoints
    .map((kp, i) => `${i + 1}. ${kp.title}${kp.content ? ` — ${kp.content}` : ""}`)
    .join("\n");

  const langInstruction = language ? `\n\nIMPORTANT: Generate ALL content in ${language === "zh" ? "Chinese (简体中文)" : "English"}. All titles, descriptions, explanations, and answers must be in ${language === "zh" ? "Chinese" : "English"}.` : "";

  try {
    const { text } = await generateText({
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
      model: textModel,
      messages: [
        {
          role: "user",
          content: `You are a study planner for the course "${courseTitle}".

Knowledge points:
${kpSummary}

Generate 1-2 study tasks per knowledge point. Return this EXACT JSON structure:
{"tasks": [{"knowledge_point_title": "exact KP title", "title": "task title", "description": "what to do", "task_type": "read", "priority": 1}]}

task_type: "read" (learn concept), "practice" (do exercises), or "review" (revisit)
priority: 1=must-know, 2=should-know, 3=nice-to-know

Return ONLY the JSON object with a "tasks" array. No other format.${langInstruction}`,
        },
      ],
    });

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");
    const raw = JSON.parse(jsonStr);
    // AI returns various formats: { tasks: [...] }, [...], or { "1": [...], "2": [...] }
    let tasks: unknown[];
    if (Array.isArray(raw)) {
      tasks = raw;
    } else if (raw.tasks && Array.isArray(raw.tasks)) {
      tasks = raw.tasks;
    } else {
      // Flatten object values: { "1": [task, task], "2": [task] } → flat array
      tasks = Object.values(raw).flat();
    }
    const parsed = studyTasksSchema.parse({ tasks });
    return parsed.tasks;
  } catch (err) {
    throw new Error(`Study task generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

// ─── Pipeline 4: Outline → Auto Quiz Questions (no exam needed) ───

export async function generateQuestionsFromOutline(
  courseTitle: string,
  knowledgePoints: { title: string; content: string | null }[],
  language?: string
): Promise<(ParsedQuestion & { matched_kp_title: string })[]> {
  const kpSummary = knowledgePoints
    .map((kp) => `- ${kp.title}${kp.content ? `: ${kp.content}` : ""}`)
    .join("\n");

  const langInstruction = language ? `\n\nIMPORTANT: Generate ALL content in ${language === "zh" ? "Chinese (简体中文)" : "English"}. All titles, descriptions, explanations, and answers must be in ${language === "zh" ? "Chinese" : "English"}.` : "";

  const autoQuizSchema = z.object({
    questions: parsedQuestionSchema
      .extend({ matched_kp_title: z.string() })
      .array(),
  });

  try {
    const { text } = await generateText({
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
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

Return ONLY valid JSON (no markdown, no code fences).${langInstruction}`,
        },
      ],
    });

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");
    const raw = JSON.parse(jsonStr);
    // Handle: { questions: [...] }, [...], or { "1": [...], "2": [...] }
    let qArr: unknown[];
    if (Array.isArray(raw)) {
      qArr = raw;
    } else if (raw.questions && Array.isArray(raw.questions)) {
      qArr = raw.questions;
    } else {
      qArr = Object.values(raw).flat();
    }
    const parsed = autoQuizSchema.parse({ questions: qArr });
    return parsed.questions;
  } catch (err) {
    throw new Error(`Question generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

// ─── Pipeline 5: Knowledge Point → Full AI Mini-Lesson ───

export async function generateLesson(
  courseTitle: string,
  knowledgePoint: { title: string; content: string | null },
  courseDescription: string,
  language?: string
): Promise<{ title: string; content: string; key_takeaways: string[]; examples: string[] }> {
  const langInstruction = language ? `\n\nIMPORTANT: Generate ALL content in ${language === "zh" ? "Chinese (简体中文)" : "English"}. All titles, descriptions, explanations, and answers must be in ${language === "zh" ? "Chinese" : "English"}.` : "";

  try {
    const { text } = await generateText({
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
      model: textModel,
      messages: [
        {
          role: "user",
          content: `You are creating a lesson for a college course called "${courseTitle}".
${courseDescription ? `Course description: ${courseDescription}` : ""}

Topic: ${knowledgePoint.title}
${knowledgePoint.content ? `Context: ${knowledgePoint.content}` : ""}

Write a complete mini-lesson that a student can learn from. Return ONLY valid JSON (no markdown fences, no extra text):

{
  "title": "Lesson title",
  "content": "Full lesson content in markdown format. Include:\\n- Clear explanation of the concept (2-3 paragraphs, student-friendly language)\\n- Use ## headers to organize sections\\n- Include code examples in \`\`\`python code blocks if it's a CS/programming topic\\n- Include worked examples with step-by-step solutions if it's math/science\\n- Use analogies and real-world connections\\n- End with a 'Think About It' question to check understanding",
  "key_takeaways": ["3-5 bullet points summarizing the most important ideas"],
  "examples": ["1-3 concrete examples or code snippets that illustrate the concept"]
}

Rules:
- Write at a college freshman level — clear but not dumbed down
- The lesson should be self-contained — a student should be able to understand the topic from this lesson alone
- If it's a programming topic, include runnable code examples
- Content should be 300-600 words (substantial but not overwhelming)
- Return ONLY the JSON object${langInstruction}`,
        },
      ],
    });

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");

    return generatedLessonSchema.parse(JSON.parse(jsonStr));
  } catch (err) {
    throw new Error(`Lesson generation failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

// ─── Pipeline 5b: Knowledge Point → Interactive Lesson Chunks (outline + parallel chunks) ───

export interface ChunkOutlineItem {
  title: string;
  teaching_goal: string;
}

export interface GeneratedChunk {
  chunk_index: number;
  content: string;
  checkpoint_type: "mcq" | "code" | "open" | "latex" | null;
  checkpoint_prompt: string | null;
  checkpoint_answer: string | null;
  checkpoint_options: { label: string; text: string }[] | null;
}

// Phase 1: Generate lesson outline (fast, ~2s)
export async function generateLessonOutline(
  courseTitle: string,
  knowledgePoint: { title: string; content: string | null },
): Promise<ChunkOutlineItem[]> {
  const { text: outlineText } = await generateText({
    model: textModel,
    messages: [{
      role: "user",
      content: `Split this knowledge point into 4 teaching sub-topics for a college Calculus II student.

Knowledge point: ${knowledgePoint.title}
${knowledgePoint.content ? `Context: ${knowledgePoint.content}` : ""}
Course: ${courseTitle}

Return JSON:
{"chunks_outline": [{"title": "...", "teaching_goal": "..."}]}

Requirements:
- 4 sub-topics, ordered from foundation to application
- Last one should be synthesis/application
- Each teaching_goal is one sentence
ONLY JSON.`,
    }],
  });

  const outlineJson = extractJSON(outlineText);
  if (!outlineJson) throw new Error("Failed to generate lesson outline");
  const outlineRaw = JSON.parse(outlineJson);
  const outline: ChunkOutlineItem[] = (outlineRaw.chunks_outline ?? []).map((item: { title?: string; teaching_goal?: string }) => ({
    title: String(item.title ?? ""),
    teaching_goal: String(item.teaching_goal ?? ""),
  }));

  if (outline.length === 0) throw new Error("Empty lesson outline");
  return outline;
}

// Phase 2: Generate a single lesson chunk
export async function generateSingleLessonChunk(
  courseTitle: string,
  outline: ChunkOutlineItem[],
  index: number,
): Promise<GeneratedChunk | null> {
  const item = outline[index];
  if (!item) return null;

  const outlineSummary = outline.map((o, i) => `${i + 1}. ${o.title}`).join("\n");
  const checkpointTypes = ["pretest", "mcq", "fill_blank", "open"] as const;
  const cpType = checkpointTypes[index % checkpointTypes.length];
  const isPretest = cpType === "pretest";

  const pretestInstruction = isPretest
    ? `IMPORTANT: This is a PRETEST chunk. Structure it as:
1. Start with a challenging question the student probably can't answer yet (this is intentional — attempting retrieval before learning enhances memory, even if they get it wrong)
2. After the checkpoint, provide the teaching content that explains the answer
The student will see "Don't worry if you don't know this yet — trying first helps you learn better" in the UI.`
    : "";

  const checkpointInstruction = cpType === "mcq" || cpType === "pretest"
    ? `checkpoint_type: "mcq" with 4 options. Wrong options based on common misconceptions.`
    : cpType === "fill_blank"
    ? `checkpoint_type: "fill_blank". checkpoint_options: null. Answer is a short phrase or number.`
    : `checkpoint_type: "open". checkpoint_options: null. Answer is 1-2 sentences. checkpoint_answer should contain the key concepts that must appear.`;

  try {
    const { text } = await generateText({
      model: textModel,
      messages: [{
        role: "user",
        content: `You are an interactive course content generator.

Full lesson outline:
${outlineSummary}

Generate part ${index + 1}: "${item.title}"
Teaching goal: ${item.teaching_goal}

Course: ${courseTitle}
Student level: College sophomore
${pretestInstruction}

Requirements:
1. content: 150-200 words, Markdown with LaTeX math ($...$). Include a concrete example.
2. checkpoint: ${checkpointInstruction}
3. Do NOT generate remediation.

Return ONLY JSON:
{"content": "markdown...", "checkpoint_type": "${cpType === "pretest" ? "mcq" : cpType}", "checkpoint_prompt": "?", "checkpoint_answer": "B", "checkpoint_options": ${cpType === "mcq" || cpType === "pretest" ? '[{"label":"A","text":"..."},{"label":"B","text":"..."},{"label":"C","text":"..."},{"label":"D","text":"..."}]' : "null"}}`,
      }],
    });

    const json = extractJSON(text);
    if (!json) return null;
    const raw = JSON.parse(json);
    return {
      chunk_index: index,
      content: String(raw.content ?? ""),
      checkpoint_type: (["mcq", "code", "open", "latex", "fill_blank"].includes(raw.checkpoint_type) ? raw.checkpoint_type : "mcq") as "mcq" | "code" | "open" | "latex" | null,
      checkpoint_prompt: raw.checkpoint_prompt ? String(raw.checkpoint_prompt) : null,
      checkpoint_answer: raw.checkpoint_answer ? String(raw.checkpoint_answer) : null,
      checkpoint_options: Array.isArray(raw.checkpoint_options) ? raw.checkpoint_options : null,
    };
  } catch {
    return null;
  }
}

// Convenience wrapper: generate outline + all chunks (blocking)
export async function generateLessonChunks(
  courseTitle: string,
  knowledgePoint: { title: string; content: string | null },
  courseDescription: string,
): Promise<{ outline: ChunkOutlineItem[]; chunks: GeneratedChunk[] }> {
  void courseDescription; // unused but kept for API compatibility
  const outline = await generateLessonOutline(courseTitle, knowledgePoint);
  const results = await Promise.all(
    outline.map((_, index) => generateSingleLessonChunk(courseTitle, outline, index))
  );
  const chunks = results.filter((c): c is GeneratedChunk => c !== null);
  if (chunks.length === 0) throw new Error("All chunk generations failed");
  return { outline, chunks };
}

// ─── Pipeline 6: Spoken Study Notes → Structured Notes + Clarifying Questions ───

const organizedStudyNoteSchema = z.object({
  title: z.string().min(1),
  summary: z.string().min(1),
  key_points: z.union([
    z.array(z.string().min(1)),
    z.string().transform((s) => [s]),
  ]).pipe(z.array(z.string()).min(2).max(6)),
  confusing_points: z.union([
    z.array(z.string().min(1)),
    z.string().transform((s) => [s]),
    z.null().transform(() => [] as string[]),
  ]).default([]),
  next_action: z.string().nullable().default(null),
  clarification_questions: z.union([
    z.array(z.string().min(1)),
    z.string().transform((s) => [s]),
    z.null().transform(() => [] as string[]),
  ]).default([]),
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
      // abortSignal: AbortSignal.timeout(AI_TIMEOUT_MS), // TEMP DISABLED
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

    const jsonStr = extractJSON(text);
    if (!jsonStr) throw new Error("AI did not return valid JSON");
    const organized = organizedStudyNoteSchema.parse(JSON.parse(jsonStr));

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
