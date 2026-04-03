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

export const parsedOutlineNodeSchema: z.ZodType<{
  title: string;
  type: "week" | "chapter" | "topic" | "knowledge_point";
  content: string | null;
  children: unknown[];
}> = z.object({
  title: z.string(),
  type: z.enum(["week", "chapter", "topic", "knowledge_point"]),
  content: z.string().nullable().default(null),
  children: z.lazy(() => parsedOutlineNodeSchema.array()).default([]),
});

export const parsedSyllabusSchema = z.object({
  title: z.string(),
  description: z.string(),
  professor: z.string().nullable().default(null),
  semester: z.string().nullable().default(null),
  nodes: parsedOutlineNodeSchema.array(),
});

export const parsedQuestionSchema = z.object({
  type: z.enum(["multiple_choice", "fill_blank", "short_answer", "true_false"]),
  stem: z.string().min(1),
  options: z.array(z.object({ label: z.string(), text: z.string() })).nullable().default(null),
  answer: z.string().min(1),
  explanation: z.string().nullable().default(null),
  difficulty: z.number().int().min(1).max(5).default(3),
});

export const attemptCreateSchema = z.object({
  question_id: z.string().uuid(),
  user_answer: z.string().min(1),
});
