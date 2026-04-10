export type CourseStatus = "active" | "archived";
export type NodeType = "week" | "chapter" | "topic" | "knowledge_point";
export type UploadType = "syllabus" | "exam" | "practice" | "notes" | "other";
export type UploadStatus = "pending" | "parsing" | "done" | "failed";
export type QuestionType = "multiple_choice" | "fill_blank" | "short_answer" | "true_false";
export type MasteryLevel = "mastered" | "reviewing" | "weak" | "untested";
export type StudyMode = "solving" | "reviewing" | "studying" | "idle";
export type NoteSource = "voice" | "text";

export interface Course {
  id: string;
  user_id: string;
  title: string;
  description: string | null;
  professor: string | null;
  semester: string | null;
  status: CourseStatus;
  created_at: string;
  updated_at: string;
}

export interface OutlineNode {
  id: string;
  course_id: string;
  parent_id: string | null;
  title: string;
  type: NodeType;
  content: string | null;
  order: number;
}

export interface Upload {
  id: string;
  course_id: string;
  file_url: string;
  file_name: string;
  file_type: string;
  upload_type: UploadType;
  parsed_content: unknown | null;
  status: UploadStatus;
  created_at: string;
}

// Answer and explanation are NOT included — they are revealed only after attempt submission
export interface Question {
  id: string;
  course_id: string;
  source_upload_id: string | null;
  knowledge_point_id: string | null;
  type: QuestionType;
  stem: string;
  options: { label: string; text: string }[] | null;
  difficulty: number;
  created_at: string;
  // Populated by GET /api/questions — user's attempt history for adaptive 85%-rule sorting
  attempt_count?: number;
  user_accuracy?: number | null;
}

// Full question with answer — only used server-side or in admin contexts
export interface QuestionWithAnswer extends Question {
  answer: string;
  explanation: string | null;
}

export interface Attempt {
  id: string;
  user_id: string;
  question_id: string;
  user_answer: string;
  is_correct: boolean;
  answered_at: string;
}

export interface ParsedSyllabus {
  title: string;
  description: string;
  professor: string | null;
  semester: string | null;
  nodes: ParsedOutlineNode[];
  missing_info: string[];
  confidence: "high" | "medium" | "low";
}

export interface ParsedOutlineNode {
  title: string;
  type: NodeType;
  content: string | null;
  children: ParsedOutlineNode[];
}

export interface ParsedQuestion {
  type: QuestionType;
  stem: string;
  options: { label: string; text: string }[] | null;
  answer: string;
  explanation: string | null;
  difficulty: number;
}

export type TaskType = "read" | "practice" | "review";
export type TaskStatus = "todo" | "done";

export interface StudyTask {
  id: string;
  course_id: string;
  knowledge_point_id: string | null;
  title: string;
  description: string;
  task_type: TaskType;
  priority: number;
  status: TaskStatus;
  order: number;
  created_at: string;
}

export interface OrganizedStudyNote {
  title: string;
  summary: string;
  key_points: string[];
  confusing_points: string[];
  next_action: string | null;
  clarification_questions: string[];
  matched_knowledge_point_id: string | null;
  matched_knowledge_point_title: string | null;
}

export interface QuestionBookmark {
  id: string;
  user_id: string;
  question_id: string;
  note: string | null;
  created_at: string;
}

export interface CourseNote {
  id: string;
  course_id: string;
  knowledge_point_id: string | null;
  knowledge_point_title: string | null;
  raw_transcript: string;
  source: NoteSource;
  title: string;
  summary: string;
  key_points: string[];
  confusing_points: string[];
  next_action: string | null;
  clarification_questions: string[];
  clarification_answers: string[];
  created_at: string;
}

export interface Lesson {
  id: string;
  course_id: string;
  knowledge_point_id: string;
  title: string;
  content: string; // markdown content
  key_takeaways: string[];
  examples: string[];
  order: number;
  created_at: string;
}

export interface ExamDate {
  id: string;
  course_id: string;
  title: string;
  exam_date: string;
  knowledge_point_ids: string[];
  created_at: string;
}

// ─── Learning System V2 Types ───

export type MasteryLevelV2 = "unseen" | "exposed" | "practiced" | "proficient" | "mastered";
export type SessionType = "teaching_challenge" | "checkpoint_open" | "study_buddy" | "review";
export type CheckpointType = "mcq" | "code" | "latex" | "open" | "canvas" | "ordering" | "fill_blank";
export type ConfidenceLevel = "none" | "surface" | "partial" | "solid" | "mastery";
export type PrerequisiteType = "hard" | "soft";

export interface ElementMastery {
  id: string;
  user_id: string;
  concept_id: string;
  element_name: string;
  times_tested: number;
  times_correct: number;
  times_non_mcq: number;
  times_non_mcq_correct: number;
  fsrs_stability: number;
  fsrs_difficulty: number;
  fsrs_retrievability: number;
  fsrs_last_review: string | null;
  current_level: MasteryLevelV2;
  level_reached_at: string;
  avg_response_time_ms: number;
  has_external_practice: boolean;
  has_non_mcq_correct: boolean;
  has_cross_concept_correct: boolean;
  has_transfer_correct: boolean;
  has_teaching_challenge_pass: boolean;
  first_contact_at: string;
  created_at: string;
  updated_at: string;
}

export interface Misconception {
  id: string;
  user_id: string;
  concept_id: string;
  misconception_description: string;
  first_seen_at: string;
  last_seen_at: string;
  occurrence_count: number;
  resolved: boolean;
  resolved_at: string | null;
  relapsed: boolean;
  relapse_count: number;
  related_concepts: string[];
  created_at: string;
}

export interface ChallengeLog {
  id: string;
  user_id: string;
  concept_id: string;
  session_type: SessionType;
  turns: unknown[];
  final_confidence: ConfidenceLevel | null;
  elements_passed: string[];
  elements_failed: string[];
  misconceptions_found: string[];
  student_self_rating: number | null;
  ai_confidence_rating: string | null;
  meta_cognition_match: boolean | null;
  created_at: string;
}

export interface TermDefinition {
  term: string;
  definition: string;
}

export interface LessonChunk {
  id: string;
  lesson_id: string;
  chunk_index: number;
  content: string;
  widget_code: string | null;
  widget_description: string | null;
  widget_challenge: string | null;
  checkpoint_type: CheckpointType | null;
  checkpoint_prompt: string | null;
  checkpoint_answer: string | null;
  checkpoint_options: { label: string; text: string }[] | null;
  checkpoint_core_elements: string[] | null;
  remediation_content: string | null;
  remediation_question: string | null;
  remediation_answer: string | null;
  key_terms: TermDefinition[] | null;
}

export interface LessonProgress {
  id: string;
  user_id: string;
  lesson_id: string;
  last_chunk_index: number;
  completed: boolean;
  checkpoint_results: Record<string, { passed: boolean; attempts: number }>;
  started_at: string;
  completed_at: string | null;
}

export interface TodayTask {
  id: string;
  type: "urgent_study" | "exam_review" | "fsrs_review" | "exam_prep" | "new_content" | "weakness";
  priority: number;
  course_id: string;
  course_title: string;
  title: string;
  description: string;
  estimated_minutes: number;
  count?: number;
  color: string;
}
