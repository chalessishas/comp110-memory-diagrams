import { z } from "zod";

export const courseCreateSchema = z.object({
  title: z.string().min(1).max(200),
  description: z.string().max(2000).nullable().default(null),
  professor: z.string().max(100).nullable().default(null),
  semester: z.string().max(50).nullable().default(null),
});

export const courseUpdateSchema = courseCreateSchema.partial().extend({
  status: z.enum(["active", "archived"]).optional(),
});

export const outlineNodeSchema = z.object({
  id: z.string().uuid(),
  parent_id: z.string().uuid().nullable(),
  title: z.string().min(1),
  type: z.enum(["week", "chapter", "topic", "knowledge_point"]),
  content: z.string().nullable().default(null),
  order: z.number().int().min(0),
});

// Accept any string for type, map unknown values to "topic"
const outlineNodeType = z.string().transform((val) => {
  const valid = ["week", "chapter", "topic", "knowledge_point"];
  return valid.includes(val) ? val as "week" | "chapter" | "topic" | "knowledge_point" : "topic" as const;
});

export const parsedOutlineNodeSchema: z.ZodType<{
  title: string;
  type: "week" | "chapter" | "topic" | "knowledge_point";
  content: string | null;
  children: unknown[];
}> = z.object({
  title: z.string(),
  type: outlineNodeType,
  content: z.string().nullable().default(null),
  children: z.lazy(() => parsedOutlineNodeSchema.array()).default([]),
});

// Fix #4: lenient confidence field — case-insensitive, unknown → "medium"
const confidenceField = z.string().transform((val) => {
  const v = val.toLowerCase();
  if (v.includes("high")) return "high" as const;
  if (v.includes("low")) return "low" as const;
  return "medium" as const;
}).default("high");

// Fix #5: missing_info — handle string instead of array, or null
const missingInfoField = z.union([
  z.array(z.string()),
  z.string().transform((s) => [s]),
  z.null().transform(() => [] as string[]),
]).default([]);

export const parsedSyllabusSchema = z.object({
  title: z.string(),
  description: z.string(),
  professor: z.string().nullable().default(null),
  semester: z.string().nullable().default(null),
  nodes: parsedOutlineNodeSchema.array(),
  missing_info: missingInfoField,
  confidence: confidenceField,
});

// Fix #2: lenient question type — normalize MCQ variants
const questionType = z.string().transform((val) => {
  const v = val.toLowerCase().replace(/[-_\s]/g, "");
  if (v.includes("multiple") || v === "mcq" || v === "mc") return "multiple_choice" as const;
  if (v.includes("fill") || v.includes("blank")) return "fill_blank" as const;
  if (v.includes("short") || v.includes("essay") || v.includes("open")) return "short_answer" as const;
  if (v.includes("true") || v.includes("false") || v.includes("tf") || v.includes("bool")) return "true_false" as const;
  return "short_answer" as const; // safe fallback
});

// Fix #3: lenient difficulty — clamp to 1-5, handle string input, handle NaN
const difficultyField = z.union([z.number(), z.string()]).transform((val) => {
  const n = typeof val === "string" ? parseInt(val, 10) : val;
  if (isNaN(n)) return 3;
  return Math.max(1, Math.min(5, Math.round(n)));
}).default(3);

// Fix #6: lenient options — handle string arrays, object maps, mixed formats
const optionsField = z.any().transform((val) => {
  if (val === null || val === undefined) return null;
  if (Array.isArray(val)) {
    return val.map((item, i) => {
      if (typeof item === "string") {
        // "A. some text" or "A) some text" format
        const match = item.match(/^([A-Da-d])[.)]\s*(.+)/);
        if (match) return { label: match[1].toUpperCase(), text: match[2] };
        return { label: String.fromCharCode(65 + i), text: item };
      }
      if (typeof item === "object" && item !== null) {
        return {
          label: String((item as Record<string, unknown>).label ?? (item as Record<string, unknown>).key ?? String.fromCharCode(65 + i)),
          text: String((item as Record<string, unknown>).text ?? (item as Record<string, unknown>).value ?? (item as Record<string, unknown>).content ?? ""),
        };
      }
      return { label: String.fromCharCode(65 + i), text: String(item) };
    });
  }
  if (typeof val === "object") {
    // {A: "foo", B: "bar"} format
    return Object.entries(val as Record<string, unknown>).map(([k, v]) => ({ label: k, text: String(v) }));
  }
  return null;
}).nullable().default(null);

export const parsedQuestionSchema = z.object({
  type: questionType,
  stem: z.string().min(1),
  options: optionsField,
  answer: z.string().min(1),
  explanation: z.string().nullable().default(null),
  difficulty: difficultyField,
});

export const attemptCreateSchema = z.object({
  question_id: z.string().uuid(),
  user_answer: z.string().min(1),
  confidence: z.union([z.literal(1), z.literal(2), z.literal(3)]).nullable().optional(),
});

export const noteOrganizeSchema = z.object({
  transcript: z.string().min(1).max(20_000),
  knowledge_point_id: z.string().uuid().nullable().optional(),
  clarification_answers: z.array(z.string().max(2_000)).max(3).default([]),
  source: z.enum(["voice", "text"]).default("voice"),
});

export const noteCreateSchema = z.object({
  knowledge_point_id: z.string().uuid().nullable().default(null),
  raw_transcript: z.string().min(1).max(20_000),
  source: z.enum(["voice", "text"]).default("voice"),
  title: z.string().min(1).max(200),
  summary: z.string().min(1).max(5_000),
  key_points: z.array(z.string().min(1).max(500)).min(1).max(8),
  confusing_points: z.array(z.string().min(1).max(500)).max(6).default([]),
  next_action: z.string().max(500).nullable().default(null),
  clarification_questions: z.array(z.string().min(1).max(500)).max(3).default([]),
  clarification_answers: z.array(z.string().min(1).max(2_000)).max(3).default([]),
});

// Fix #7: lenient generatedLessonSchema — defaults + handle string-instead-of-array
export const generatedLessonSchema = z.object({
  title: z.string().default("Untitled Lesson"),
  content: z.string().default(""),
  key_takeaways: z.union([
    z.array(z.string()),
    z.string().transform((s) => [s]),
  ]).default([]),
  examples: z.union([
    z.array(z.string()),
    z.string().transform((s) => [s]),
  ]).default([]),
}).passthrough();
