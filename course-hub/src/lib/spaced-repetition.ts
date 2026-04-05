// Simplified FSRS (Free Spaced Repetition Scheduler)
// Based on the algorithm used by Anki's FSRS-4.5

export interface ReviewCard {
  question_id: string;
  stability: number;    // days until 90% recall probability
  difficulty: number;   // 0-1, how hard this card is
  due_date: string;     // ISO date string
  last_review: string;  // ISO date string
  reps: number;         // number of reviews
  lapses: number;       // number of times forgotten
}

export type Rating = 1 | 2 | 3 | 4; // 1=Again, 2=Hard, 3=Good, 4=Easy

const DECAY = -0.5;
const FACTOR = 19 / 81;

export function nextInterval(stability: number, requestedRetention: number = 0.9): number {
  return Math.max(1, Math.round(stability * (Math.pow(requestedRetention, 1 / DECAY) - 1) / FACTOR));
}

export function newCard(questionId: string): ReviewCard {
  const now = new Date().toISOString();
  return {
    question_id: questionId,
    stability: 1,
    difficulty: 0.3,
    due_date: now,
    last_review: now,
    reps: 0,
    lapses: 0,
  };
}

export function reviewCard(card: ReviewCard, rating: Rating): ReviewCard {
  const now = new Date();
  const nowISO = now.toISOString();

  let newStability: number;
  let newDifficulty = card.difficulty;
  let lapses = card.lapses;

  if (rating === 1) {
    // Again — forgot
    lapses += 1;
    newStability = Math.max(0.5, card.stability * 0.2);
    newDifficulty = Math.min(1, card.difficulty + 0.1);
  } else if (rating === 2) {
    // Hard
    newStability = card.stability * 1.2;
    newDifficulty = Math.min(1, card.difficulty + 0.05);
  } else if (rating === 3) {
    // Good
    newStability = card.stability * (1.5 + (1 - card.difficulty));
    newDifficulty = Math.max(0, card.difficulty - 0.02);
  } else {
    // Easy
    newStability = card.stability * (2.5 + (1 - card.difficulty));
    newDifficulty = Math.max(0, card.difficulty - 0.05);
  }

  const interval = nextInterval(newStability);
  const dueDate = new Date(now);
  dueDate.setDate(dueDate.getDate() + interval);

  return {
    question_id: card.question_id,
    stability: newStability,
    difficulty: newDifficulty,
    due_date: dueDate.toISOString(),
    last_review: nowISO,
    reps: card.reps + 1,
    lapses,
  };
}

export function getDueCards(cards: ReviewCard[]): ReviewCard[] {
  const now = new Date();
  return cards
    .filter((c) => new Date(c.due_date) <= now)
    .sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
}

export function getNextReviewDate(cards: ReviewCard[]): Date | null {
  if (cards.length === 0) return null;
  const sorted = [...cards].sort((a, b) => new Date(a.due_date).getTime() - new Date(b.due_date).getTime());
  return new Date(sorted[0].due_date);
}

// Storage in localStorage (per-user, client-side)
const STORAGE_KEY = "coursehub.review-cards";

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
  const card = newCard(questionId);
  saveCards([...cards, card]);
  return card;
}

export function updateCard(questionId: string, rating: Rating): ReviewCard {
  const cards = loadCards();
  const idx = cards.findIndex((c) => c.question_id === questionId);
  const card = idx >= 0 ? cards[idx] : newCard(questionId);
  const updated = reviewCard(card, rating);
  if (idx >= 0) {
    cards[idx] = updated;
  } else {
    cards.push(updated);
  }
  saveCards(cards);
  return updated;
}
