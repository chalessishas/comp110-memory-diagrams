import { createClient } from "@/lib/supabase/server";
import { attemptCreateSchema } from "@/lib/schemas";
import { checkRateLimit } from "@/lib/rate-limit";
import { evaluateLevel } from "@/lib/mastery-v2";
import type { MasteryStats } from "@/lib/mastery-v2";
import type { MasteryLevelV2 } from "@/types";
import { NextResponse } from "next/server";

export async function POST(request: Request) {
  const supabase = await createClient();
  const { data: { user } } = await supabase.auth.getUser();
  if (!user) return NextResponse.json({ error: "Unauthorized" }, { status: 401 });

  // Rate limit: prevents flooding the attempts table to game adaptive difficulty sorting
  if (!await checkRateLimit(`attempts:${user.id}`, 60, 60_000)) {
    return NextResponse.json({ error: "Rate limit exceeded" }, { status: 429 });
  }

  const body = await request.json();
  const parsed = attemptCreateSchema.safeParse(body);
  if (!parsed.success) return NextResponse.json({ error: parsed.error.flatten() }, { status: 400 });

  const { data: question } = await supabase
    .from("questions")
    .select("answer, type, explanation, stem, knowledge_point_id")
    .eq("id", parsed.data.question_id)
    .single();

  if (!question) return NextResponse.json({ error: "Question not found" }, { status: 404 });

  const ua = parsed.data.user_answer.trim().toLowerCase().replace(/[.,;:!?'"()]/g, "").replace(/\s+/g, " ");
  const ea = question.answer.trim().toLowerCase().replace(/[.,;:!?'"()]/g, "").replace(/\s+/g, " ");

  let isCorrect: boolean;
  if (question.type === "short_answer") {
    // Key-term overlap: correct if ≥50% of meaningful answer words are present
    const userWords = new Set(ua.split(/\s+/));
    const answerWords = ea.split(/\s+/).filter((w: string) => w.length > 3);
    const matchCount = answerWords.filter((w: string) => userWords.has(w)).length;
    isCorrect = answerWords.length > 0 ? matchCount / answerWords.length >= 0.5 : ua.length > 0;
  } else if (question.type === "fill_blank") {
    // Fuzzy match: exact, contains, or numeric comparison
    if (ua === ea) { isCorrect = true; }
    else if (ua.includes(ea) || ea.includes(ua)) { isCorrect = true; }
    else {
      const uNum = parseFloat(ua), eNum = parseFloat(ea);
      isCorrect = !isNaN(uNum) && !isNaN(eNum) && Math.abs(uNum - eNum) < 0.001;
    }
  } else {
    isCorrect = ua === ea;
  }

  const { data, error } = await supabase
    .from("attempts")
    .insert({
      user_id: user.id,
      question_id: parsed.data.question_id,
      user_answer: parsed.data.user_answer,
      is_correct: isCorrect,
      confidence: parsed.data.confidence ?? null,
    })
    .select()
    .single();

  if (error) return NextResponse.json({ error: error.message }, { status: 500 });

  // Keep mastery attempt counters current — required for exposed→practiced evaluation
  // Only updates existing rows (lesson completion creates the initial "exposed" record)
  let postUpdateAccuracy: number | null = null;
  let postUpdateTested = 0;
  if (question.knowledge_point_id) {
    const { data: mastery } = await supabase
      .from("element_mastery")
      .select("id, current_level, times_tested, times_correct, times_non_mcq, times_non_mcq_correct, has_non_mcq_correct, has_external_practice, has_cross_concept_correct, has_transfer_correct, has_teaching_challenge_pass, fsrs_stability, fsrs_retrievability, first_contact_at, level_reached_at")
      .eq("user_id", user.id)
      .eq("concept_id", question.knowledge_point_id)
      .maybeSingle();

    if (mastery) {
      postUpdateTested = mastery.times_tested + 1;
      const postUpdateCorrect = mastery.times_correct + (isCorrect ? 1 : 0);
      postUpdateAccuracy = postUpdateCorrect / postUpdateTested;

      // fill_blank and short_answer require free recall — count as non-MCQ
      const isNonMcq = question.type === "fill_blank" || question.type === "short_answer";
      const newHasNonMcqCorrect = mastery.has_non_mcq_correct || (isNonMcq && isCorrect);
      // short_answer correct = transfer evidence (free construction > MCQ recognition, Roediger & Butler 2011)
      const newHasTransferCorrect = mastery.has_transfer_correct || (question.type === "short_answer" && isCorrect);
      const updates: Record<string, unknown> = {
        times_tested: postUpdateTested,
        times_correct: postUpdateCorrect,
        has_external_practice: true, // any attempt via this route is outside lesson context
        updated_at: new Date().toISOString(),
      };
      if (isNonMcq) {
        updates.times_non_mcq = (mastery.times_non_mcq ?? 0) + 1;
        if (isCorrect) {
          updates.times_non_mcq_correct = (mastery.times_non_mcq_correct ?? 0) + 1;
          updates.has_non_mcq_correct = true;
        }
      }
      if (newHasTransferCorrect && !mastery.has_transfer_correct) {
        updates.has_transfer_correct = true;
      }

      // Evaluate mastery level transition with all available data.
      // recentAccuracy uses overall accuracy as an approximation (no extra query needed).
      // courseConceptsAtLevel2OrAbove=0 and hasDownstreamDependents=false make crossConceptOk
      // always pass — avoids an expensive count query on every attempt.
      const stats: MasteryStats = {
        currentLevel: mastery.current_level as MasteryLevelV2,
        timesTested: postUpdateTested,
        timesCorrect: postUpdateCorrect,
        timesNonMcq: (mastery.times_non_mcq ?? 0) + (isNonMcq ? 1 : 0),
        timesNonMcqCorrect: (mastery.times_non_mcq_correct ?? 0) + (isNonMcq && isCorrect ? 1 : 0),
        hasExternalPractice: true,
        hasNonMcqCorrect: newHasNonMcqCorrect,
        hasCrossConceptCorrect: mastery.has_cross_concept_correct ?? false,
        hasTransferCorrect: newHasTransferCorrect,
        hasTeachingChallengePass: mastery.has_teaching_challenge_pass ?? false,
        fsrsStability: mastery.fsrs_stability ?? 0,
        fsrsRetrievability: mastery.fsrs_retrievability ?? 1,
        firstContactAt: new Date(mastery.first_contact_at ?? Date.now()),
        levelReachedAt: new Date(mastery.level_reached_at ?? Date.now()),
        recentAccuracy: postUpdateAccuracy,
        recentCount: Math.min(postUpdateTested, 5),
        courseConceptsAtLevel2OrAbove: 0,
        hasDownstreamDependents: false,
      };

      const levelResult = evaluateLevel(stats, false);
      if (levelResult.changed) {
        updates.current_level = levelResult.newLevel;
        updates.level_reached_at = new Date().toISOString();
      }

      await supabase
        .from("element_mastery")
        .update(updates)
        .eq("id", mastery.id);
    }
  }

  // Track misconceptions: auto-log wrong answers, auto-resolve when accuracy recovers.
  // Resolve threshold: ≥75% accuracy over ≥5 attempts on the knowledge point.
  if (question.knowledge_point_id) {
    if (!isCorrect) {
      const { data: existing } = await supabase
        .from("misconceptions")
        .select("id, occurrence_count, resolved, relapse_count")
        .eq("user_id", user.id)
        .eq("concept_id", question.knowledge_point_id)
        .maybeSingle();

      if (existing) {
        await supabase
          .from("misconceptions")
          .update({
            occurrence_count: existing.occurrence_count + 1,
            last_seen_at: new Date().toISOString(),
            ...(existing.resolved
              ? { resolved: false, relapsed: true, relapse_count: existing.relapse_count + 1 }
              : {}),
          })
          .eq("id", existing.id);
      } else {
        const desc = question.stem
          ? question.stem.slice(0, 120)
          : "Repeated errors on this topic";
        await supabase.from("misconceptions").insert({
          user_id: user.id,
          concept_id: question.knowledge_point_id,
          misconception_description: desc,
        });
      }
    } else if (postUpdateAccuracy !== null && postUpdateAccuracy >= 0.75 && postUpdateTested >= 5) {
      // Correct answer pushed accuracy above threshold — resolve any open misconception
      await supabase
        .from("misconceptions")
        .update({ resolved: true, resolved_at: new Date().toISOString() })
        .eq("user_id", user.id)
        .eq("concept_id", question.knowledge_point_id)
        .eq("resolved", false);
    }
  }

  // Reveal answer + explanation only after submission
  return NextResponse.json({
    ...data,
    correct_answer: question.answer,
    explanation: question.explanation ?? null,
  }, { status: 201 });
}
