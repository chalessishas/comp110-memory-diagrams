import type { CourseNote, NoteSource, OrganizedStudyNote } from "@/types";

export interface CourseNoteRow {
  id: string;
  course_id: string;
  knowledge_point_id: string | null;
  source: NoteSource;
  raw_transcript: string;
  title: string;
  summary: string;
  key_points: unknown;
  confusing_points: unknown;
  next_action: string | null;
  clarification_questions: unknown;
  clarification_answers: unknown;
  created_at: string;
}

export interface CourseNoteCreatePayload {
  knowledge_point_id: string | null;
  raw_transcript: string;
  source: NoteSource;
  title: string;
  summary: string;
  key_points: string[];
  confusing_points: string[];
  next_action: string | null;
  clarification_questions: string[];
  clarification_answers: string[];
}

function asStringArray(value: unknown) {
  if (!Array.isArray(value)) return [];
  return value.filter((item): item is string => typeof item === "string");
}

export function toCourseNote(
  row: CourseNoteRow,
  knowledgePointTitle: string | null
): CourseNote {
  return {
    id: row.id,
    course_id: row.course_id,
    knowledge_point_id: row.knowledge_point_id,
    knowledge_point_title: knowledgePointTitle,
    raw_transcript: row.raw_transcript,
    source: row.source,
    title: row.title,
    summary: row.summary,
    key_points: asStringArray(row.key_points),
    confusing_points: asStringArray(row.confusing_points),
    next_action: row.next_action,
    clarification_questions: asStringArray(row.clarification_questions),
    clarification_answers: asStringArray(row.clarification_answers),
    created_at: row.created_at,
  };
}

export function toCourseNoteCreatePayload({
  knowledgePointId,
  transcript,
  source,
  organized,
  clarificationAnswers,
}: {
  knowledgePointId: string | null;
  transcript: string;
  source: NoteSource;
  organized: OrganizedStudyNote;
  clarificationAnswers: string[];
}): CourseNoteCreatePayload {
  return {
    knowledge_point_id: knowledgePointId,
    raw_transcript: transcript,
    source,
    title: organized.title,
    summary: organized.summary,
    key_points: organized.key_points,
    confusing_points: organized.confusing_points,
    next_action: organized.next_action,
    clarification_questions: organized.clarification_questions,
    clarification_answers: clarificationAnswers.filter((answer) => answer.trim().length > 0),
  };
}
