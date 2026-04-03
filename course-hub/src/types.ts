export type CourseStatus = "active" | "archived";
export type NodeType = "week" | "chapter" | "topic" | "knowledge_point";
export type UploadType = "syllabus" | "exam" | "practice" | "notes" | "other";
export type UploadStatus = "pending" | "parsing" | "done" | "failed";
export type QuestionType = "multiple_choice" | "fill_blank" | "short_answer" | "true_false";
export type MasteryLevel = "mastered" | "reviewing" | "weak" | "untested";

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

export interface Question {
  id: string;
  course_id: string;
  source_upload_id: string | null;
  knowledge_point_id: string | null;
  type: QuestionType;
  stem: string;
  options: { label: string; text: string }[] | null;
  answer: string;
  explanation: string | null;
  difficulty: number;
  created_at: string;
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
