import type {
  Course,
  Question,
  Attempt,
  OutlineNode,
  ExamDate,
  StudyTask,
  Lesson,
  LessonChunk,
  CourseNote,
  QuestionBookmark,
  ElementMastery,
  TodayTask,
} from "@/types";

// ─── Core fetch wrapper ───

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public body: unknown,
  ) {
    super(`API ${status}: ${typeof body === "object" && body && "error" in body ? (body as { error: string }).error : statusText}`);
    this.name = "ApiError";
  }
}

async function apiFetch<T>(
  path: string,
  init?: RequestInit & { params?: Record<string, string | number | boolean | undefined> },
): Promise<T> {
  const { params, ...fetchInit } = init ?? {};

  let url = path.startsWith("/") ? path : `/${path}`;
  if (params) {
    const sp = new URLSearchParams();
    for (const [k, v] of Object.entries(params)) {
      if (v !== undefined) sp.set(k, String(v));
    }
    const qs = sp.toString();
    if (qs) url += `?${qs}`;
  }

  const res = await fetch(url, {
    ...fetchInit,
    headers: { "Content-Type": "application/json", ...fetchInit.headers },
  });

  if (!res.ok) {
    const body = await res.json().catch(() => null);
    throw new ApiError(res.status, res.statusText, body);
  }

  const text = await res.text();
  return text ? JSON.parse(text) : (null as T);
}

// ─── Courses ───

export const courses = {
  list: () => apiFetch<Course[]>("/api/courses"),

  get: (id: string) => apiFetch<Course>(`/api/courses/${id}`),

  create: (data: { title: string; description?: string; professor?: string; semester?: string }) =>
    apiFetch<Course>("/api/courses", { method: "POST", body: JSON.stringify(data) }),

  update: (id: string, data: Partial<Pick<Course, "title" | "description" | "professor" | "semester" | "status">>) =>
    apiFetch<Course>(`/api/courses/${id}`, { method: "PUT", body: JSON.stringify(data) }),

  delete: (id: string) => apiFetch<void>(`/api/courses/${id}`, { method: "DELETE" }),
};

// ─── Questions ───

export const questions = {
  list: (courseId: string, knowledgePointId?: string) =>
    apiFetch<Question[]>("/api/questions", { params: { courseId, ...(knowledgePointId && { knowledgePointId }) } }),

  generate: (courseId: string) =>
    apiFetch<{ questions: Question[] }>(`/api/courses/${courseId}/generate`, { method: "POST" }),
};

// ─── Attempts ───

export const attempts = {
  submit: (data: { question_id: string; user_answer: string }) =>
    apiFetch<Attempt & { is_correct: boolean; correct_answer: string; explanation: string | null }>(
      "/api/attempts",
      { method: "POST", body: JSON.stringify(data) },
    ),
};

// ─── Outline Nodes ───

export const outlineNodes = {
  list: (courseId: string) =>
    apiFetch<OutlineNode[]>("/api/outline-nodes", { params: { courseId } }),
};

// ─── Exams ───

export const exams = {
  list: (courseId: string) =>
    apiFetch<ExamDate[]>(`/api/courses/${courseId}/exams`),
};

// ─── Study Tasks ───

export const studyTasks = {
  list: (courseId: string) =>
    apiFetch<StudyTask[]>(`/api/courses/${courseId}/study-tasks`),
};

// ─── Lessons ───

export const lessons = {
  list: (courseId: string) =>
    apiFetch<Lesson[]>(`/api/courses/${courseId}/lessons`),

  chunks: (lessonId: string) =>
    apiFetch<LessonChunk[]>(`/api/courses/lessons/${lessonId}/chunks`),
};

// ─── Notes ───

export const notes = {
  list: (courseId: string) =>
    apiFetch<CourseNote[]>(`/api/courses/${courseId}/notes`),
};

// ─── Bookmarks ───

export const bookmarks = {
  list: () => apiFetch<QuestionBookmark[]>("/api/bookmarks"),

  toggle: (questionId: string, note?: string) =>
    apiFetch<QuestionBookmark>("/api/bookmarks", {
      method: "POST",
      body: JSON.stringify({ question_id: questionId, note }),
    }),
};

// ─── Mastery ───

export const mastery = {
  get: (courseId: string) =>
    apiFetch<ElementMastery[]>(`/api/courses/${courseId}/mastery`),
};

// ─── Dashboard ───

export const dashboard = {
  today: () => apiFetch<TodayTask[]>("/api/courses/today-tasks"),
};

// Re-export error class for catch blocks
export { ApiError };
