import { createEmptyCard, fsrs, generatorParameters, Rating, type Card, type ReviewLog } from "ts-fsrs";

const STORAGE_KEY = "coursehub.review-cards";

const params = generatorParameters({ request_retention: 0.9 });
const scheduler = fsrs(params);

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
  const result = scheduler.repeat(reviewCard.card, now);
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
  return reviewCard;
}

export function getDueCards(cards: ReviewCard[]): ReviewCard[] {
  const now = new Date();
  return cards
    .filter((c) => new Date(c.card.due) <= now)
    .sort((a, b) => new Date(a.card.due).getTime() - new Date(b.card.due).getTime());
}

export function getNextReviewDate(cards: ReviewCard[]): Date | null {
  if (cards.length === 0) return null;
  const sorted = [...cards].sort((a, b) => new Date(a.card.due).getTime() - new Date(b.card.due).getTime());
  return new Date(sorted[0].card.due);
}
