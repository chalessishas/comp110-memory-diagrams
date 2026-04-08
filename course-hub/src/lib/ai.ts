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
// Timeout: rely on Vercel maxDuration (60s) — DashScope doesn't handle AbortSignal cleanly

// ─── Shared infrastructure ───

const SYSTEM_JSON = `You are a structured data generator. Output ONLY valid JSON — no markdown fences, no prose, no <think> blocks. If you are unsure about a field, use null rather than omitting it.`;

const SYSTEM_EDUCATOR = `You are an expert course content creator. Write at a college level — clear but not dumbed down. Output ONLY valid JSON.`;

function langSuffix(language?: string): string {
  if (!language) return "";
  return language === "zh"
    ? "\n\nIMPORTANT: Generate ALL content in Chinese (简体中文)."
    : "\n\nIMPORTANT: Generate ALL content in English.";
}

// AbortController disabled — DashScope's OpenAI-compatible API doesn't handle abort cleanly
// Relying on Vercel's maxDuration (60s) as the hard timeout instead

async function withRetry<T>(fn: () => Promise<T>, retries = 1): Promise<T> {
  try { return await fn(); }
  catch (err) {
    if (retries <= 0) throw err;
    return withRetry(fn, retries - 1);
  }
}

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

  try {
    return await withRetry(async () => {
      const { text } = await generateText({
        model: visionModel,
        temperature: 0.2,
        maxOutputTokens: 8192,
        system: SYSTEM_JSON,
        messages: [{
          role: "user",
          content: [
            { type: "file", data: `data:${mimeType};base64,${fileBase64}`, mediaType: mimeType as "application/pdf" },
            { type: "text", text: `Analyze this course syllabus and extract its structure as a NESTED hierarchy.

Return JSON: { title, description, professor (null if not found), semester (null if not found), confidence ("high"/"medium"/"low"), missing_info (array), nodes }

Each node: { title, type, content (null if obvious), children }
Types: "week", "chapter", "topic", "knowledge_point"

CRITICAL: Every week/chapter MUST have children. Leaf nodes must be type "knowledge_point".${langSuffix(language)}` },
          ],
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      return parsedSyllabusSchema.parse(JSON.parse(jsonStr)) as ParsedSyllabus;
    });
  } catch (err) {
    throw new Error(`Syllabus parsing failed: ${err instanceof Error ? err.message : "Unknown error"}`);
  }
}

export async function parseSyllabusText(rawText: string, language?: string): Promise<ParsedSyllabus> {
  try {
    return await withRetry(async () => {
      const { text } = await generateText({
        model: textModel,
        temperature: 0.2,
        maxOutputTokens: 8192,

        system: SYSTEM_JSON,
        messages: [{
          role: "user",
          content: `Extract ACTUAL teaching content from this syllabus as a nested hierarchy.

RULES:
1. Only extract EXPLICITLY mentioned topics. Do NOT invent.
2. Skip administrative content (grading, attendance).
3. Every week/chapter MUST have children. "Integration by parts, Partial fractions" = TWO separate knowledge_point children.
4. Hierarchy: week/chapter → topic → knowledge_point. Leaf = "knowledge_point".
5. No detailed schedule → confidence: "low".

JSON shape:
{"title":"...","description":"...","professor":"name or null","semester":"... or null","confidence":"high|medium|low","missing_info":[],"nodes":[{"title":"Week 1: Functions","type":"week","content":null,"children":[{"title":"Domain and range","type":"knowledge_point","content":"Determining domain and range","children":[]}]}]}

Course text:
"""
${rawText}
"""${langSuffix(language)}`,
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      return parsedSyllabusSchema.parse(JSON.parse(jsonStr)) as ParsedSyllabus;
    });
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
    return await withRetry(async () => {
      const { text } = await generateText({
        model: visionModel,
        temperature: 0.2,
        maxOutputTokens: 8192,
        system: SYSTEM_JSON,
        messages: [{
          role: "user",
          content: [
            { type: "file", data: `data:${mimeType};base64,${fileBase64}`, mediaType: mimeType as "application/pdf" },
            { type: "text", text: `Extract all questions from this exam document. Per question:
- type: "multiple_choice" | "fill_blank" | "short_answer" | "true_false"
- stem, options ({label,text} array or null), answer, explanation, difficulty (1-5)
- matched_kp_title: match to one of: [${kpList}], or null

Return {"questions": [...]}` },
          ],
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      const raw = JSON.parse(jsonStr);
      const wrapped = Array.isArray(raw) ? { questions: raw } : raw;
      return questionsSchema.parse(wrapped).questions;
    });
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
    return await withRetry(async () => {
      const { text } = await generateText({
        model: textModel,
        temperature: 0.4,
        maxOutputTokens: 4096,

        system: SYSTEM_JSON,
        messages: [{
          role: "user",
          content: `Study planner for "${courseTitle}".

Knowledge points:
${kpSummary}

Generate 1-2 tasks per KP. Return:
{"tasks": [{"knowledge_point_title": "exact KP title", "title": "...", "description": "...", "task_type": "read|practice|review", "priority": 1}]}
priority: 1=must-know, 2=should-know, 3=nice-to-know${langSuffix(language)}`,
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      const raw = JSON.parse(jsonStr);
      let tasks: unknown[];
      if (Array.isArray(raw)) tasks = raw;
      else if (raw.tasks && Array.isArray(raw.tasks)) tasks = raw.tasks;
      else tasks = Object.values(raw).flat();
      return studyTasksSchema.parse({ tasks }).tasks;
    });
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
    return await withRetry(async () => {
      const { text } = await generateText({
        model: textModel,
        temperature: 0.5,
        maxOutputTokens: 8192,

        system: SYSTEM_EDUCATOR,
        messages: [{
          role: "user",
          content: `Create practice questions for "${courseTitle}".

Knowledge points:
${kpSummary}

Generate 2-3 questions per KP. Mix types:
- multiple_choice: 4 options (A/B/C/D), one correct
- fill_blank: key term blanked
- true_false: [{label:"True",text:"True"},{label:"False",text:"False"}]
- short_answer: 1-2 sentence answer

Per question: stem, options (or null), answer, explanation, difficulty (1-5), matched_kp_title (exact match from list above).

Test understanding, not memorization. Return {"questions": [...]}${langSuffix(language)}`,
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      const raw = JSON.parse(jsonStr);
      let qArr: unknown[];
      if (Array.isArray(raw)) qArr = raw;
      else if (raw.questions && Array.isArray(raw.questions)) qArr = raw.questions;
      else qArr = Object.values(raw).flat();
      return autoQuizSchema.parse({ questions: qArr }).questions;
    });
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
    return await withRetry(async () => {
      const { text } = await generateText({
        model: textModel,
        temperature: 0.6,
        maxOutputTokens: 4096,

        system: SYSTEM_EDUCATOR,
        messages: [{
          role: "user",
          content: `Create a mini-lesson for "${courseTitle}".${courseDescription ? ` (${courseDescription})` : ""}

Topic: ${knowledgePoint.title}
${knowledgePoint.content ? `Context: ${knowledgePoint.content}` : ""}

Return JSON:
{"title": "...", "content": "markdown, 300-600 words, ## headers, code/math examples, analogies, ends with comprehension question", "key_takeaways": ["3-5 points"], "examples": ["1-3 concrete examples"]}

Self-contained lesson. College level.${langSuffix(language)}`,
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      return generatedLessonSchema.parse(JSON.parse(jsonStr));
    });
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
  key_terms: { term: string; definition: string }[] | null;
}

// Detect course domain to pick appropriate teaching strategy
function detectCourseType(courseTitle: string): "stem" | "humanities" | "general" {
  const title = courseTitle.toLowerCase();
  const stemKeywords = ["calculus", "physics", "chemistry", "math", "statistics", "biology", "engineering", "algorithm", "programming", "cs ", "computer science", "linear algebra", "differential", "organic", "data structure"];
  const humanitiesKeywords = ["literature", "history", "philosophy", "psychology", "sociology", "political", "economics", "writing", "english", "art ", "music", "language", "communication", "law"];
  if (stemKeywords.some(k => title.includes(k))) return "stem";
  if (humanitiesKeywords.some(k => title.includes(k))) return "humanities";
  return "general";
}

const TEACHING_STRATEGIES = {
  stem: `4 sub-topics following CONCRETENESS FADING (Fyfe et al. 2015):
  1. Pretest: concrete real-world scenario (physical quantities, money, distances)
  2. Concrete worked example with specific numbers
  3. Symbolic/formulaic generalization with variables
  4. Transfer: apply to a different context`,
  humanities: `4 sub-topics following CASE-BASED REASONING:
  1. Pretest: opinion/prediction question about a real scenario
  2. Primary source or case study analysis
  3. Framework/theory that explains the pattern
  4. Transfer: apply framework to a new case`,
  general: `4 sub-topics following PROGRESSIVE COMPLEXITY:
  1. Pretest: intuition check with everyday example
  2. Core concept with concrete illustration
  3. Nuances, exceptions, and deeper analysis
  4. Transfer: real-world application in different context`,
} as const;

// Phase 1: Generate lesson outline (fast, ~2s)
export async function generateLessonOutline(
  courseTitle: string,
  knowledgePoint: { title: string; content: string | null },
): Promise<ChunkOutlineItem[]> {
  const courseType = detectCourseType(courseTitle);
  const strategy = TEACHING_STRATEGIES[courseType];

  return withRetry(async () => {
    const { text: outlineText } = await generateText({
      model: textModel,
      temperature: 0.3,
      maxOutputTokens: 2048,
      system: SYSTEM_JSON,
      messages: [{
        role: "user",
        content: `Split this knowledge point into 4 teaching sub-topics for a college student.

Knowledge point: ${knowledgePoint.title}
${knowledgePoint.content ? `Context: ${knowledgePoint.content}` : ""}
Course: ${courseTitle}

Return: {"chunks_outline": [{"title": "...", "teaching_goal": "one sentence"}]}

Teaching strategy:
${strategy}`,
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
  });
}

// Phase 2: Generate a single lesson chunk
export async function generateSingleLessonChunk(
  courseTitle: string,
  outline: ChunkOutlineItem[],
  index: number,
): Promise<GeneratedChunk | null> {
  const item = outline[index];
  if (!item) return null;

  const courseType = detectCourseType(courseTitle);
  const outlineSummary = outline.map((o, i) => `${i + 1}. ${o.title}`).join("\n");
  const checkpointTypes = ["pretest", "mcq", "fill_blank", "open"] as const;
  const cpType = checkpointTypes[index % checkpointTypes.length];
  const isPretest = cpType === "pretest";

  const ABSTRACTION_LEVELS = {
    stem: [
      "CONCRETE SCENARIO: Real-world scenario with physical quantities/money/rates. No abstract symbols — only numbers and words.",
      "CONCRETE EXAMPLE: Worked example with numbers. Introduce notation alongside concrete values.",
      "SYMBOLIC: General formula/method with variables. Reference the earlier concrete example.",
      "TRANSFER: Apply to a different context. Same deep structure, new surface form.",
    ],
    humanities: [
      "HOOK: Engaging question or surprising fact about a real case/event.",
      "CASE STUDY: Detailed analysis of a primary source, historical event, or real scenario.",
      "FRAMEWORK: Introduce the theoretical lens or analytical framework that explains the pattern.",
      "TRANSFER: Apply the framework to a different case or contemporary issue.",
    ],
    general: [
      "INTUITION: Everyday example that builds intuition. No jargon yet.",
      "CORE CONCEPT: Clear explanation with concrete illustration.",
      "NUANCE: Deeper analysis — exceptions, edge cases, common misconceptions.",
      "TRANSFER: Apply to a real-world situation the student might encounter.",
    ],
  } as const;

  const levels = ABSTRACTION_LEVELS[courseType];
  const abstractionInstruction = levels[index] ?? levels[levels.length - 1];

  const pretestInstruction = isPretest
    ? `This is a PRETEST: start with a question the student probably can't answer yet. After checkpoint, provide teaching content. Retrieval attempt before learning enhances memory.`
    : "";

  const checkpointInstruction = cpType === "mcq" || cpType === "pretest"
    ? `checkpoint_type: "mcq", 4 options, wrong options from common misconceptions.`
    : cpType === "fill_blank"
    ? `checkpoint_type: "fill_blank", checkpoint_options: null, answer is short phrase/number.`
    : `checkpoint_type: "open", checkpoint_options: null, answer 1-2 sentences with key concepts.`;

  try {
    return await withRetry(async () => {
      const { text } = await generateText({
        model: textModel,
        temperature: 0.5,
        maxOutputTokens: 2048,

        system: SYSTEM_EDUCATOR,
        messages: [{
          role: "user",
          content: `Lesson outline: ${outlineSummary}

Generate part ${index + 1}: "${item.title}" — ${item.teaching_goal}
Course: ${courseTitle}
${pretestInstruction}

1. content: 150-200 words, Markdown + LaTeX ($...$)
2. Abstraction: ${abstractionInstruction}
3. ${checkpointInstruction}
4. key_terms: 2-5 domain terms with 1-sentence definitions

Return JSON:
{"content":"...","checkpoint_type":"${cpType === "pretest" ? "mcq" : cpType}","checkpoint_prompt":"?","checkpoint_answer":"...","checkpoint_options":${cpType === "mcq" || cpType === "pretest" ? '[{"label":"A","text":"..."},...]' : "null"},"key_terms":[{"term":"...","definition":"..."}]}`,
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
        key_terms: Array.isArray(raw.key_terms) ? raw.key_terms.filter((t: unknown) => t && typeof t === "object" && "term" in (t as Record<string, unknown>) && "definition" in (t as Record<string, unknown>)) : null,
      };
    });
  } catch { return null; }
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
    const organized = await withRetry(async () => {
      const { text } = await generateText({
        model: textModel,
        temperature: 0.3,
        maxOutputTokens: 2048,

        system: SYSTEM_JSON,
        messages: [{
          role: "user",
          content: `Organize a student's spoken note for "${courseTitle}".

Knowledge points: ${kpSummary}
${selectedKnowledgePointTitle ? `Tagged to: ${selectedKnowledgePointTitle}` : "No manual tag."}

Spoken note:
"""
${transcript}
"""

Clarifications: ${clarificationContext}

Return: {"title":"...","summary":"2-4 sentences","key_points":["2-6 items"],"confusing_points":["unclear parts"],"next_action":"one step or null","clarification_questions":["0-3 if ambiguous"],"matched_kp_title":"exact KP title or null"}

Preserve student's meaning. Don't invent facts. If manual tag exists, use it as matched_kp_title. If answers resolve ambiguity, return empty clarification_questions.`,
        }],
      });
      const jsonStr = extractJSON(text);
      if (!jsonStr) throw new Error("AI did not return valid JSON");
      return organizedStudyNoteSchema.parse(JSON.parse(jsonStr));
    });

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
