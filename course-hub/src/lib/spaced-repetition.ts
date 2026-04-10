import { createEmptyCard, fsrs, generatorParameters, Rating, type Card, type ReviewLog } from "ts-fsrs";

const STORAGE_KEY = "coursehub.review-cards";
const EXAM_DATE_KEY = "coursehub.exam-date";
const EXAM_SCOPE_KEY = "coursehub.exam-scope"; // per-course: { courseId: string[] (KP IDs) }

function getExamModeParams() {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(EXAM_DATE_KEY);
  if (!raw) return null;
  const examDate = new Date(raw);
  const now = new Date();
  const daysUntilExam = Math.max(1, Math.ceil((examDate.getTime() - now.getTime()) / 86400000));
  if (daysUntilExam > 30) return null; // only activate within 30 days of exam
  return { request_retention: 0.95, maximum_interval: daysUntilExam };
}

let _scheduler: ReturnType<typeof fsrs> | null = null;
let _lastExamKey: string | null = null;

function getScheduler() {
  const examKey = typeof window !== "undefined" ? localStorage.getItem(EXAM_DATE_KEY) : null;
  if (!_scheduler || examKey !== _lastExamKey) {
    _lastExamKey = examKey ?? null;
    const ep = getExamModeParams();
    _scheduler = fsrs(generatorParameters(ep ?? { request_retention: 0.9 }));
  }
  return _scheduler;
}

export { Rating } from "ts-fsrs";
export type { Card } from "ts-fsrs";

export interface ReviewCard {
  question_id: string;
  card: Card;
  log: ReviewLog[];
}

export function loadCards(): ReviewCard[] {
  if (typeof window === "undefined") return [];
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? JSON.parse(raw) : [];
  } catch { return []; }
}

export function saveCards(cards: ReviewCard[]) {
  if (typeof window === "undefined") return;
  localStorage.setItem(STORAGE_KEY, JSON.stringify(cards));
}

export function getOrCreateCard(questionId: string): ReviewCard {
  const cards = loadCards();
  const existing = cards.find((c) => c.question_id === questionId);
  if (existing) return existing;

  const card: ReviewCard = {
    question_id: questionId,
    card: createEmptyCard(),
    log: [],
  };
  saveCards([...cards, card]);
  return card;
}

export function updateCard(questionId: string, rating: Rating): ReviewCard {
  const cards = loadCards();
  const idx = cards.findIndex((c) => c.question_id === questionId);

  let reviewCard: ReviewCard;
  if (idx >= 0) {
    reviewCard = cards[idx];
  } else {
    reviewCard = { question_id: questionId, card: createEmptyCard(), log: [] };
  }

  const now = new Date();
  const result = getScheduler().repeat(reviewCard.card, now);
  // Rating.Manual (5) is not schedulable; callers should only pass Again/Hard/Good/Easy
  const scheduled = result[rating as 1 | 2 | 3 | 4];

  reviewCard.card = scheduled.card;
  reviewCard.log.push(scheduled.log);

  if (idx >= 0) {
    cards[idx] = reviewCard;
  } else {
    cards.push(reviewCard);
  }
  saveCards(cards);
  // Fire-and-forget server sync — non-blocking, failure is silent (localStorage is fallback)
  syncCardToServer(questionId, scheduled.card, scheduled.log);
  return reviewCard;
}

// Serialize a ts-fsrs Card + optional ReviewLog and POST to server.
// Called after every review; non-blocking.
export function syncCardToServer(questionId: string, card: Card, log?: ReviewLog): void {
  if (typeof window === "undefined") return;
  const cardPayload = {
    question_id: questionId,
    due: card.due instanceof Date ? card.due.toISOString() : card.due,
    stability: card.stability,
    difficulty: card.difficulty,
    elapsed_days: card.elapsed_days,
    scheduled_days: card.scheduled_days,
    reps: card.reps,
    lapses: card.lapses,
    learning_steps: card.learning_steps,
    state: card.state as number,
    last_review: card.last_review
      ? (card.last_review instanceof Date ? card.last_review.toISOString() : card.last_review)
      : null,
  };
  const body: { cards: typeof cardPayload[]; logs?: object[] } = { cards: [cardPayload] };
  if (log) {
    body.logs = [{
      question_id: questionId,
      rating: log.rating as number,
      state: log.state as number,
      due: log.due instanceof Date ? log.due.toISOString() : log.due,
      stability: log.stability,
      difficulty: log.difficulty,
      elapsed_days: log.elapsed_days,
      last_elapsed_days: log.last_elapsed_days,
      scheduled_days: log.scheduled_days,
      reviewed_at: log.review instanceof Date ? log.review.toISOString() : log.review,
    }];
  }
  fetch("/api/fsrs", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  }).catch(() => { /* silent — localStorage is the fallback */ });
}

// Pull card states for a course from server and merge into localStorage.
// DB wins over localStorage on reps tie; higher reps = more recent reviews wins.
// Called once on course page mount for authenticated users.
export async function pullCardsFromServer(courseId: string): Promise<void> {
  if (typeof window === "undefined") return;
  try {
    const res = await fetch(`/api/fsrs?courseId=${courseId}`);
    if (!res.ok) return;
    const { cards: serverCards } = await res.json() as {
      cards: Array<{
        question_id: string; due: string; stability: number; difficulty: number;
        elapsed_days: number; scheduled_days: number; reps: number; lapses: number;
        learning_steps: number; state: number; last_review: string | null;
      }>
    };
    if (!serverCards?.length) return;

    const local = loadCards();
    const localMap = new Map(local.map((c) => [c.question_id, c]));

    for (const sc of serverCards) {
      const existing = localMap.get(sc.question_id);
      // Server wins if it has more reps or equal reps (server is source of truth)
      if (!existing || sc.reps >= existing.card.reps) {
        localMap.set(sc.question_id, {
          question_id: sc.question_id,
          card: {
            due: new Date(sc.due),
            stability: sc.stability,
            difficulty: sc.difficulty,
            elapsed_days: sc.elapsed_days,
            scheduled_days: sc.scheduled_days,
            reps: sc.reps,
            lapses: sc.lapses,
            learning_steps: sc.learning_steps ?? 0,
            state: sc.state as Card["state"],
            last_review: sc.last_review ? new Date(sc.last_review) : undefined,
          },
          log: existing?.log ?? [],
        });
      }
    }

    saveCards(Array.from(localMap.values()));
  } catch { /* silent — localStorage is the fallback */ }
}

export function getDueCards(cards: ReviewCard[]): ReviewCard[] {
  const now = new Date();
  return cards
    .filter((c) => new Date(c.card.due) <= now)
    .sort((a, b) => new Date(a.card.due).getTime() - new Date(b.card.due).getTime());
}

// Exam-optimized queue: ALL reviewed cards sorted by ascending retrievability on exam day.
// Cards predicted to be well-remembered (>= 0.95) on exam day are excluded — time is better
// spent on weak cards. New/unreviewed cards are included at the front.
export function getExamPriorityCards(cards: ReviewCard[]): ReviewCard[] {
  const examDate = getExamDate();
  if (!examDate) return getDueCards(cards);

  const scheduler = getScheduler();
  const scored: { card: ReviewCard; retrieval: number }[] = [];

  for (const c of cards) {
    // New cards (never reviewed) get retrieval = 0 — highest priority
    if (c.card.reps === 0) {
      scored.push({ card: c, retrieval: 0 });
      continue;
    }
    const r = scheduler.get_retrievability(c.card, examDate, false) as number;
    if (r < 0.95) scored.push({ card: c, retrieval: r });
  }

  return scored
    .sort((a, b) => a.retrieval - b.retrieval)
    .map(s => s.card);
}

// Get a card's predicted retrievability on exam day (for UI display)
export function getExamDayRetrievability(card: ReviewCard): number | null {
  const examDate = getExamDate();
  if (!examDate || card.card.reps === 0) return null;
  return getScheduler().get_retrievability(card.card, examDate, false) as number;
}

// Interleave items so adjacent items have different keys when possible.
// Uses a bounded lookahead (default 5) to preserve the original priority ordering
// while avoiding same-key adjacency. If no different-key item is found within the
// lookahead window, the highest-priority item is taken as-is.
// Rationale: Brunmair & Richter 2019 meta-analysis found g=0.42 for interleaving;
// Taylor & Rohrer 2010 found d=1.21 in math classrooms.
export function interleaveByKey<T>(items: T[], keyFn: (item: T) => string | null | undefined, lookahead = 5): T[] {
  if (items.length <= 2) return items;

  const result: T[] = [];
  const remaining = [...items];
  let lastKey: string | null | undefined = null;

  while (remaining.length > 0) {
    const searchLen = Math.min(remaining.length, lookahead);
    let picked = -1;

    for (let i = 0; i < searchLen; i++) {
      if (keyFn(remaining[i]) !== lastKey || lastKey == null) {
        picked = i;
        break;
      }
    }

    if (picked === -1) picked = 0;

    const [item] = remaining.splice(picked, 1);
    result.push(item);
    lastKey = keyFn(item);
  }

  return result;
}

export function getNextReviewDate(cards: ReviewCard[]): Date | null {
  if (cards.length === 0) return null;
  const sorted = [...cards].sort((a, b) => new Date(a.card.due).getTime() - new Date(b.card.due).getTime());
  return new Date(sorted[0].card.due);
}

export function setExamDate(date: Date | null) {
  if (typeof window === "undefined") return;
  if (date) {
    localStorage.setItem(EXAM_DATE_KEY, date.toISOString());
  } else {
    localStorage.removeItem(EXAM_DATE_KEY);
  }
}

export function getExamDate(): Date | null {
  if (typeof window === "undefined") return null;
  const raw = localStorage.getItem(EXAM_DATE_KEY);
  return raw ? new Date(raw) : null;
}

export function isExamMode(): boolean {
  const exam = getExamDate();
  if (!exam) return false;
  const days = Math.ceil((exam.getTime() - Date.now()) / 86400000);
  return days >= 0 && days <= 30;
}

export function daysUntilExam(): number | null {
  const exam = getExamDate();
  if (!exam) return null;
  const days = Math.ceil((exam.getTime() - Date.now()) / 86400000);
  return days >= 0 ? Math.max(1, days) : null;
}

// ── Exam Scope: filter content to specific knowledge points ──

export function getExamScope(courseId: string): string[] | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(EXAM_SCOPE_KEY);
    if (!raw) return null;
    const scopes: Record<string, string[]> = JSON.parse(raw);
    return scopes[courseId] ?? null;
  } catch { return null; }
}

export function setExamScope(courseId: string, kpIds: string[] | null) {
  if (typeof window === "undefined") return;
  try {
    const raw = localStorage.getItem(EXAM_SCOPE_KEY);
    const scopes: Record<string, string[]> = raw ? JSON.parse(raw) : {};
    if (kpIds && kpIds.length > 0) {
      scopes[courseId] = kpIds;
    } else {
      delete scopes[courseId];
    }
    localStorage.setItem(EXAM_SCOPE_KEY, JSON.stringify(scopes));
  } catch { /* ignore */ }
}

export function hasExamScope(courseId: string): boolean {
  return (getExamScope(courseId) ?? []).length > 0;
}
