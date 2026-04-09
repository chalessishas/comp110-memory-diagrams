// ═══════════════════════════════════════════════════════════════
// Multi-Model Configuration for Benchmark Comparison
// ═══════════════════════════════════════════════════════════════
//
// Updated: 2026-04-09 — verified against official docs for each provider.
// Models organized by price tier. All use @ai-sdk/openai adapter
// (OpenAI-compatible APIs) unless noted otherwise.
//
// Usage:
//   DASHSCOPE_API_KEY=xxx DEEPSEEK_API_KEY=yyy OPENAI_API_KEY=zzz \
//   GEMINI_API_KEY=aaa ANTHROPIC_API_KEY=bbb \
//   npx tsx tests/ai-benchmark/compare-models.ts

import { createOpenAI } from "@ai-sdk/openai";
import { generateText } from "ai";

export interface ModelConfig {
  id: string;
  name: string;
  provider: string;
  pricePerMInput: number;   // $ per 1M input tokens
  pricePerMOutput: number;  // $ per 1M output tokens
  envKey: string;           // env var name for API key
  baseURL: string;
  modelId: string;
  available: boolean;       // set at runtime based on env var presence
  tier: "ultra-cheap" | "budget" | "mid-range" | "premium";
  notes?: string;
}

// ─── Tier 1: Ultra-cheap ($0.10-$0.20/M input) ─────────────
// Good for: volume testing, quality floor measurement

// ─── Tier 2: Budget ($0.25-$0.60/M input) ───────────────────
// Good for: production candidates for CourseHub

// ─── Tier 3: Mid-range ($0.75-$3.00/M input) ────────────────
// Good for: quality ceiling reference

// ─── Tier 4: Premium ($5+/M input) ──────────────────────────
// Good for: absolute quality benchmark

export const MODELS: ModelConfig[] = [
  // ────────── Tier 1: Ultra-cheap ──────────
  {
    id: "gpt-4.1-nano",
    name: "GPT-4.1 Nano",
    provider: "OpenAI",
    pricePerMInput: 0.10,
    pricePerMOutput: 0.40,
    envKey: "OPENAI_API_KEY",
    baseURL: "https://api.openai.com/v1",
    modelId: "gpt-4.1-nano",
    available: false,
    tier: "ultra-cheap",
    notes: "1M+ context, structured outputs, ultra-cheap",
  },
  {
    id: "gemini-2.5-flash-lite",
    name: "Gemini 2.5 Flash-Lite",
    provider: "Google",
    pricePerMInput: 0.10,
    pricePerMOutput: 0.40,
    envKey: "GEMINI_API_KEY",
    baseURL: "https://generativelanguage.googleapis.com/v1beta/openai",
    modelId: "gemini-2.5-flash-lite",
    available: false,
    tier: "ultra-cheap",
    notes: "1M context, GA stable, cheapest Google model",
  },
  {
    id: "gpt-5.4-nano",
    name: "GPT-5.4 Nano",
    provider: "OpenAI",
    pricePerMInput: 0.20,
    pricePerMOutput: 1.25,
    envKey: "OPENAI_API_KEY",
    baseURL: "https://api.openai.com/v1",
    modelId: "gpt-5.4-nano",
    available: false,
    tier: "ultra-cheap",
    notes: "400K context, latest gen, structured outputs",
  },

  // ────────── Tier 2: Budget (production candidates) ──────────
  {
    id: "qwen3.5-plus",
    name: "Qwen 3.5-Plus ★ PRODUCTION",
    provider: "DashScope (Alibaba)",
    pricePerMInput: 0.26,
    pricePerMOutput: 1.56,
    envKey: "DASHSCOPE_API_KEY",
    baseURL: "https://dashscope.aliyuncs.com/compatible-mode/v1",
    modelId: "qwen3.5-plus",
    available: false,
    tier: "budget",
    notes: "Current CourseHub production model. MoE 17B active. Best Chinese quality/price",
  },
  {
    id: "deepseek-chat",
    name: "DeepSeek V3.2",
    provider: "DeepSeek",
    pricePerMInput: 0.27,
    pricePerMOutput: 1.10,
    envKey: "DEEPSEEK_API_KEY",
    baseURL: "https://api.deepseek.com/v1",
    modelId: "deepseek-chat",
    available: false,
    tier: "budget",
    notes: "V3.2 (Dec 2025). 64K context. Strong reasoning at low cost",
  },
  {
    id: "gemini-2.5-flash",
    name: "Gemini 2.5 Flash",
    provider: "Google",
    pricePerMInput: 0.30,
    pricePerMOutput: 2.50,
    envKey: "GEMINI_API_KEY",
    baseURL: "https://generativelanguage.googleapis.com/v1beta/openai",
    modelId: "gemini-2.5-flash",
    available: false,
    tier: "budget",
    notes: "1M context, GA stable, controllable thinking budgets",
  },
  {
    id: "gpt-4.1-mini",
    name: "GPT-4.1 Mini",
    provider: "OpenAI",
    pricePerMInput: 0.40,
    pricePerMOutput: 1.60,
    envKey: "OPENAI_API_KEY",
    baseURL: "https://api.openai.com/v1",
    modelId: "gpt-4.1-mini",
    available: false,
    tier: "budget",
    notes: "1M+ context, structured outputs, widely used",
  },
  {
    id: "o4-mini",
    name: "OpenAI o4-mini",
    provider: "OpenAI",
    pricePerMInput: 0.55,
    pricePerMOutput: 2.20,
    envKey: "OPENAI_API_KEY",
    baseURL: "https://api.openai.com/v1",
    modelId: "o4-mini",
    available: false,
    tier: "budget",
    notes: "Reasoning model. Replaced o3-mini. Good for complex question generation",
  },
  {
    id: "deepseek-reasoner",
    name: "DeepSeek V3.2 Reasoner",
    provider: "DeepSeek",
    pricePerMInput: 0.55,
    pricePerMOutput: 2.19,
    envKey: "DEEPSEEK_API_KEY",
    baseURL: "https://api.deepseek.com/v1",
    modelId: "deepseek-reasoner",
    available: false,
    tier: "budget",
    notes: "V3.2 thinking mode (incl. R1 capabilities). 64K + 32K CoT",
  },

  // ────────── Tier 3: Mid-range (quality reference) ──────────
  {
    id: "gpt-5.4-mini",
    name: "GPT-5.4 Mini",
    provider: "OpenAI",
    pricePerMInput: 0.75,
    pricePerMOutput: 4.50,
    envKey: "OPENAI_API_KEY",
    baseURL: "https://api.openai.com/v1",
    modelId: "gpt-5.4-mini",
    available: false,
    tier: "mid-range",
    notes: "400K context, latest gen mid-tier, structured outputs",
  },
  {
    id: "claude-haiku-4.5",
    name: "Claude Haiku 4.5",
    provider: "Anthropic (OpenAI-compat)",
    pricePerMInput: 1.00,
    pricePerMOutput: 5.00,
    envKey: "ANTHROPIC_API_KEY",
    baseURL: "https://api.anthropic.com/v1/",
    modelId: "claude-haiku-4-5",
    available: false,
    tier: "mid-range",
    notes: "200K context, fastest Claude. OpenAI-compat endpoint (no structured outputs)",
  },
  {
    id: "gemini-2.5-pro",
    name: "Gemini 2.5 Pro",
    provider: "Google",
    pricePerMInput: 1.25,
    pricePerMOutput: 10.00,
    envKey: "GEMINI_API_KEY",
    baseURL: "https://generativelanguage.googleapis.com/v1beta/openai",
    modelId: "gemini-2.5-pro",
    available: false,
    tier: "mid-range",
    notes: "1M context, GA stable, strong reasoning/math/science",
  },
  {
    id: "claude-sonnet-4.6",
    name: "Claude Sonnet 4.6",
    provider: "Anthropic (OpenAI-compat)",
    pricePerMInput: 3.00,
    pricePerMOutput: 15.00,
    envKey: "ANTHROPIC_API_KEY",
    baseURL: "https://api.anthropic.com/v1/",
    modelId: "claude-sonnet-4-6",
    available: false,
    tier: "mid-range",
    notes: "1M context, best speed/intelligence balance. OpenAI-compat endpoint",
  },

  // ────────── Tier 4: Premium (quality ceiling) ──────────
  {
    id: "claude-opus-4.6",
    name: "Claude Opus 4.6",
    provider: "Anthropic (OpenAI-compat)",
    pricePerMInput: 5.00,
    pricePerMOutput: 25.00,
    envKey: "ANTHROPIC_API_KEY",
    baseURL: "https://api.anthropic.com/v1/",
    modelId: "claude-opus-4-6",
    available: false,
    tier: "premium",
    notes: "1M context, most intelligent Claude. Quality ceiling reference",
  },
];

// Check which models have API keys available
export function getAvailableModels(): ModelConfig[] {
  return MODELS.map(m => ({
    ...m,
    available: !!process.env[m.envKey],
  })).filter(m => m.available);
}

// Get models by tier
export function getModelsByTier(tier: ModelConfig["tier"]): ModelConfig[] {
  return MODELS.filter(m => m.tier === tier);
}

// Create a generation function for a specific model
export function createModelGenerator(config: ModelConfig) {
  const provider = createOpenAI({
    baseURL: config.baseURL,
    apiKey: process.env[config.envKey] ?? "",
  });
  const model = provider(config.modelId);

  return async function generate(
    courseTitle: string,
    kps: { title: string; content: string | null }[],
  ) {
    const kpSummary = kps
      .map((kp) => `- ${kp.title}${kp.content ? `: ${kp.content}` : ""}`)
      .join("\n");

    // Same prompt as generateQuestionsFromOutline in ai.ts (post-improvement version)
    const { text } = await generateText({
      model,
      messages: [{
        role: "user",
        content: `You are creating practice questions for the course "${courseTitle}".

Knowledge points:
${kpSummary}

Generate 2-3 practice questions per knowledge point. Mix question types:
- multiple_choice: 4 options (A/B/C/D), exactly one correct
- fill_blank: leave a key term blank for the student to fill
- true_false: 2 options [{"label":"True","text":"True"},{"label":"False","text":"False"}]
- short_answer: open-ended, 1-2 sentence answer expected

Each question must have:
- A clear, unambiguous stem
- A correct answer
- explanation: Explain WHY the answer is correct. Then identify the most likely wrong reasoning a student might have and explain why it fails. (2-3 sentences minimum)
- difficulty: 1-5 calibrated as follows:
  1 = Recall: identify or define a term
  2 = Understand: explain a concept in own words, interpret a diagram
  3 = Apply: use a formula/method in a straightforward problem
  4 = Analyze: compare approaches, identify relationships, multi-step reasoning
  5 = Evaluate/Create: critique a solution, design an approach, justify a choice
- bloom_level: tag as "remember", "understand", "apply", "analyze", "evaluate", or "create"
- matched_kp_title: exactly matching one of the knowledge point titles listed above

Question design rules:
- At least one question per KP must be Apply level or above (not just recall/definition)
- For multiple_choice: base WRONG options on real student misconceptions, not random facts. Each distractor should represent a specific error in reasoning that a student might actually make.
- Make questions test understanding, not just memorization.

Return ONLY valid JSON (no markdown, no code fences).`,
      }],
    });

    // Parse JSON (same logic as ai.ts extractJSON)
    const cleaned = text
      .replace(/<think>[\s\S]*?<\/think>/g, "")
      .replace(/```(?:json)?\s*/g, "")
      .replace(/```\s*/g, "");
    const objMatch = cleaned.match(/\{[\s\S]*\}/);
    const arrMatch = cleaned.match(/\[[\s\S]*\]/);
    const jsonStr = objMatch?.[0] ?? arrMatch?.[0];

    if (!jsonStr) throw new Error("No JSON found in response");
    const raw = JSON.parse(jsonStr);

    let qArr: unknown[];
    if (Array.isArray(raw)) qArr = raw;
    else if (raw.questions && Array.isArray(raw.questions)) qArr = raw.questions;
    else qArr = Object.values(raw).flat();

    // Lightweight parse (don't use Zod here — we want to see raw AI output quality)
    return qArr.map((q: unknown) => {
      const item = q as Record<string, unknown>;
      return {
        type: String(item.type ?? "short_answer"),
        stem: String(item.stem ?? ""),
        options: Array.isArray(item.options) ? item.options as { label: string; text: string }[] : null,
        answer: String(item.answer ?? ""),
        explanation: item.explanation ? String(item.explanation) : null,
        difficulty: Number(item.difficulty ?? 3),
        bloom_level: String(item.bloom_level ?? "understand"),
        matched_kp_title: String(item.matched_kp_title ?? ""),
      };
    });
  };
}
