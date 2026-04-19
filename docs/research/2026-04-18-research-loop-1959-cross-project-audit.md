# Research Loop — 2026-04-18 19:59 Cross-Project Audit

**Trigger**: Automated Research Loop (new day — 23.5h since last code activity)
**Agent**: sonnet-0418b

---

## Fleet Status Snapshot

| Project | State | Blocker |
|---------|-------|---------|
| TOEFL | ✅ Done | None |
| ai-text-detector | 🟡 HOLD | API keys + product direction (DeepSeek-only vs general) |
| Signal-Map | 🔴 HOLD | Supabase env vars (master-gated) |
| chronicle | 🟢 Active | None |
| course-hub | 🔴 HOLD | User authorization needed |

---

## TOEFL: Coverage Gap Analysis

Current routes implemented:
- `/reading` — Full Academic passages (vocab, purpose, prose_summary, inference, multiple-select, multiple-choice)
- `/writing` — Build sentence, Write email, Academic Discussion (Task 2)

**Gaps identified:**
1. **Integrated Writing (Task 1)** — Read passage → listen to lecture → write response. Requires audio content. Master-gated.
2. **Listening section** — Entirely missing. Requires audio files. Master-gated.
3. **Speaking section** — Entirely missing. Requires mic access + prompt delivery. Master-gated.

**Immediately actionable (no user input needed):**
- Add "Reading: Fill in a Table" question type (categorize facts into a 2-column table). Already supported by data.js patterns — would be ~80 lines new component code.
- Grammar section (CompleteWords.jsx) covers L1-L68. Could autonomously extend to L70-L80 with new patterns.

---

## ai-text-detector: Free Multi-Model Data Options

Blocker: Path C script needs API keys for GPT-4o / Claude / Gemini.

**Free/cheap alternatives researched from knowledge base:**
1. **Ollama local models** — llama3, mistral, qwen2.5 can generate unlimited samples locally. No API key needed. Speed: ~10-50 tok/s on M-series Mac. Feasible for 20K-50K samples per model family.
2. **HuggingFace Inference API (free tier)** — 1K requests/day free. Models: Llama-3-8B, Mistral-7B, Qwen2-7B. Sufficient for diversity sampling, not volume.
3. **Together.ai** — $5 free credit, ~$0.0002/1K tokens. 20K samples × 200 tok = $0.80. Cost-effective.

**Recommendation for user**: If goal is general AI detector, use Ollama (zero cost) to generate Llama-3 + Mistral + Qwen samples locally. Script can run overnight. Adds 3 new model families without API keys or cost.

**Autonomous action possible**: Update `build_dataset_v6.py` to add Ollama provider path (no API key required, just `ollama serve` running locally). Can write the code, but cannot run it without user confirming Ollama is installed.

---

## Signal-Map: Prisma 7 Migration (Code-Only)

STATUS.md notes: `package.json#prisma` config is deprecated in Prisma 7, needs `prisma.config.ts`.

**Migration scope** (offline, no DB needed):
1. Move `prisma: { schema: "..." }` from package.json → `prisma.config.ts`
2. Update `npx prisma` commands in README/STATUS.md

This is a ~10-line mechanical change. Can be done autonomously without DB connectivity. **Risk**: Low — config migration is well-documented and reversible. Worth doing to eliminate the deprecation warning.

---

## Proposed Actions (Priority Order)

1. **[Can do now]** Signal-Map Prisma 7 config migration (~10 lines, no DB needed)
2. **[Can do now]** TOEFL Reading: Add "Fill in a Table" question type component
3. **[Needs Ollama check]** ai-text-detector: Add Ollama provider to build_dataset_v6.py
4. **[Master-gated]** ai-text-detector product direction: DeepSeek-only vs general
5. **[Master-gated]** Signal-Map: Supabase env vars for testing
