import { createClient } from "@/lib/supabase/server";
import { checkRateLimit } from "@/lib/rate-limit";
import { NextResponse } from "next/server";
import { z } from "zod";

// FSRS Card state schema — mirrors ts-fsrs Card interface primitives
const cardStateSchema = z.object({
  question_id: z.string().uuid(),
  due: z.string().datetime(),
  stability: z.number(),
  difficulty: z.number(),
  elapsed_days: z.number().int(),
  scheduled_days: z.number().int(),
  reps: z.number().int(),
  lapses: z.number().int(),
  learning_steps: z.number().int().default(0),
  state: z.number().int().min(0).max(3), // 0=New,1=Learning,2=Review,3=Relearning
  last_review: z.string().datetime().nullable().optional(),
});

// ReviewLog entry schema — immutable append-only record per review
const reviewLogSchema = z.object({
  question_id: z.string().uuid(),
  rating: z.number().int().min(1).max(4),
  state: z.number().int().min(0).max(3),
  due: z.string().datetime(),
  stability: z.number(),
  difficulty: z.number(),
  elapsed_days: z.number().int(),
  last_elapsed_days: z.number().int(),
  scheduled_days: z.number().int(),
  reviewed_at: z.string().datetime(),
});

const syncBodySchema = z.object({
  cards: z.array(cardStateSchema),
  logs: z.array(reviewLogSchema).optional().default([]),
});

// POST /api/fsrs — upsert card states + append review logs (client → server sync)
export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // 120/min — generous for fast reviewers (2 cards/sec), blocks bulk flooding
  if (!await checkRateLimit(`fsrs-sync:${user.id}`, 120, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const body = await request.json();
  const parsed = syncBodySchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const { cards, logs } = parsed.data;
  const now = new Date().toISOString();

  // Upsert card states — DB is source of truth, last-write wins on conflict
  if (cards.length > 0) {
    const { error } = await supabase.from("fsrs_cards").upsert(
      cards.map((c) => ({
        user_id: user.id,
        question_id: c.question_id,
        due: c.due,
        stability: c.stability,
        difficulty: c.difficulty,
        elapsed_days: c.elapsed_days,
        scheduled_days: c.scheduled_days,
        reps: c.reps,
        lapses: c.lapses,
        learning_steps: c.learning_steps,
        state: c.state,
        last_review: c.last_review ?? null,
        updated_at: now,
      })),
      { onConflict: "user_id,question_id" }
    );
    if (error) return NextResponse.json({ error: error.message }, { status: 500 });

    // Propagate FSRS stability + retrievability to element_mastery so mastery-v2
    // can evaluate practiced→proficient (requires fsrsStability >= 7) and
    // run downgrade checks (fsrsRetrievability < 0.70).
    // Strategy: MAX stability per KP across all synced questions for that KP.
    const questionIds = cards.map((c) => c.question_id);
    const { data: qRows } = await supabase
      .from("questions")
      .select("id, knowledge_point_id")
      .in("id", questionIds);

    if (qRows && qRows.length > 0) {
      // Build kp_id → {maxStability, latestReview} map
      const kpMap = new Map<string, { stability: number; lastReview: string | null }>();
      for (const q of qRows) {
        if (!q.knowledge_point_id) continue;
        const card = cards.find((c) => c.question_id === q.id);
        if (!card) continue;
        const existing = kpMap.get(q.knowledge_point_id);
        if (!existing || card.stability > existing.stability) {
          kpMap.set(q.knowledge_point_id, {
            stability: card.stability,
            lastReview: card.last_review ?? null,
          });
        }
      }

      // Update element_mastery rows — one update per distinct KP
      const dayMs = 86_400_000;
      await Promise.all(
        Array.from(kpMap.entries()).map(([kpId, { stability, lastReview }]) => {
          const daysSince = lastReview
            ? (Date.now() - new Date(lastReview).getTime()) / dayMs
            : 0;
          // FSRS retrievability: R = (1 + t / (9 * S))^-1
          const retrievability = stability > 0
            ? Math.pow(1 + daysSince / (9 * stability), -1)
            : 0;
          return supabase
            .from("element_mastery")
            .update({
              fsrs_stability: stability,
              fsrs_retrievability: Math.round(retrievability * 1000) / 1000,
              fsrs_last_review: lastReview,
              updated_at: now,
            })
            .eq("user_id", user.id)
            .eq("concept_id", kpId)
            .eq("element_name", "_overall");
        })
      );
    }
  }

  // Append review logs — insert only new entries (idempotent by reviewed_at + question_id)
  if (logs.length > 0) {
    await supabase.from("fsrs_review_logs").upsert(
      logs.map((l) => ({
        user_id: user.id,
        question_id: l.question_id,
        rating: l.rating,
        state: l.state,
        due: l.due,
        stability: l.stability,
        difficulty: l.difficulty,
        elapsed_days: l.elapsed_days,
        last_elapsed_days: l.last_elapsed_days,
        scheduled_days: l.scheduled_days,
        reviewed_at: l.reviewed_at,
      })),
      { onConflict: "user_id,question_id,reviewed_at", ignoreDuplicates: true }
    );
    // ignoreDuplicates: retry storms silently skip already-logged entries
  }

  return NextResponse.json({ synced: cards.length, logs: logs.length });
}

// GET /api/fsrs?courseId=X — fetch server card states for a course (server → client)
export async function GET(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // 30/min — one pull per course page load; burst protection
  if (!await checkRateLimit(`fsrs-fetch:${user.id}`, 30, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const { searchParams } = new URL(request.url);
  const courseId = searchParams.get("courseId");
  if (!courseId) return NextResponse.json({ error: "courseId required" }, { status: 400 });

  // Get all question IDs for the course, then fetch matching card states
  const { data: questions } = await supabase
    .from("questions")
    .select("id")
    .eq("course_id", courseId);

  const questionIds = (questions ?? []).map((q) => q.id);
  if (questionIds.length === 0) return NextResponse.json({ cards: [] });

  const { data: cards, error } = await supabase
    .from("fsrs_cards")
    .select("question_id, due, stability, difficulty, elapsed_days, scheduled_days, reps, lapses, learning_steps, state, last_review")
    .eq("user_id", user.id)
    .in("question_id", questionIds);

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  return NextResponse.json({ cards: cards ?? [] });
}
