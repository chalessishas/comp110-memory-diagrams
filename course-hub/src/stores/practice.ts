import { create } from "zustand";
import type { Question } from "@/types";
import { questions as questionsApi, attempts as attemptsApi } from "@/lib/api";

type PracticeStatus = "idle" | "loading" | "answering" | "feedback" | "complete";

interface AttemptResult {
  isCorrect: boolean;
  correctAnswer: string;
  explanation: string | null;
}

interface PracticeState {
  // Data
  courseId: string | null;
  questions: Question[];
  currentIndex: number;
  status: PracticeStatus;
  error: string | null;

  // Current answer
  selectedAnswer: string;
  attemptResult: AttemptResult | null;

  // Session stats
  totalAnswered: number;
  totalCorrect: number;

  // Actions
  loadQuestions: (courseId: string) => Promise<void>;
  selectAnswer: (answer: string) => void;
  submitAnswer: () => Promise<void>;
  nextQuestion: () => void;
  reset: () => void;
}

const initialState = {
  courseId: null,
  questions: [],
  currentIndex: 0,
  status: "idle" as PracticeStatus,
  error: null,
  selectedAnswer: "",
  attemptResult: null,
  totalAnswered: 0,
  totalCorrect: 0,
};

export const usePracticeStore = create<PracticeState>((set, get) => ({
  ...initialState,

  loadQuestions: async (courseId: string) => {
    set({ ...initialState, courseId, status: "loading" });
    try {
      const data = await questionsApi.list(courseId);
      if (data.length === 0) {
        set({ status: "complete", error: "No questions available for this course." });
        return;
      }
      // Shuffle questions for practice variety
      const shuffled = [...data].sort(() => Math.random() - 0.5);
      set({ questions: shuffled, status: "answering" });
    } catch (e) {
      set({ status: "idle", error: e instanceof Error ? e.message : "Failed to load questions" });
    }
  },

  selectAnswer: (answer: string) => {
    if (get().status !== "answering") return;
    set({ selectedAnswer: answer });
  },

  submitAnswer: async () => {
    const { questions, currentIndex, selectedAnswer, status } = get();
    if (status !== "answering" || !selectedAnswer) return;

    const question = questions[currentIndex];
    set({ status: "loading" });

    try {
      const result = await attemptsApi.submit({
        question_id: question.id,
        user_answer: selectedAnswer,
      });
      set((s) => ({
        status: "feedback",
        attemptResult: {
          isCorrect: result.is_correct,
          correctAnswer: result.correct_answer,
          explanation: result.explanation,
        },
        totalAnswered: s.totalAnswered + 1,
        totalCorrect: s.totalCorrect + (result.is_correct ? 1 : 0),
      }));
    } catch (e) {
      set({ status: "answering", error: e instanceof Error ? e.message : "Failed to submit answer" });
    }
  },

  nextQuestion: () => {
    const { currentIndex, questions } = get();
    if (currentIndex + 1 >= questions.length) {
      set({ status: "complete" });
      return;
    }
    set({
      currentIndex: currentIndex + 1,
      status: "answering",
      selectedAnswer: "",
      attemptResult: null,
    });
  },

  reset: () => set(initialState),
}));
