# Research Loop — 2026-04-18 20:25 Tech Audit

**Trigger**: Automated Research Loop (stable HOLD, fleet idle post Phase 1 delivery)
**Agent**: sonnet-0418i (sub-agent WebSearch)

---

## 1. Next.js 15 + Tailwind v4 — comp110 Phase 2 Setup Guide

**Tailwind v4.2 shipped April 2026** (current). Key changes vs v3:

| Item | v3 | v4 |
|------|----|----|
| Config file | `tailwind.config.js` | Eliminated — config lives in CSS via `@theme {}` |
| CSS import | `@tailwind base/components/utilities` | `@import "tailwindcss"` |
| PostCSS plugin | JS-based | Rust/Oxide engine — `@tailwindcss/postcss` |
| Content scanning | Manual `content: [...]` array | Auto-scans project |
| Webpack | Not official | Webpack plugin added in v4.2 |

**For comp110 Phase 2 (Next.js 15 App Router)**:
```bash
npm install tailwindcss@latest @tailwindcss/postcss@latest
```
```js
// postcss.config.mjs
export default { plugins: { '@tailwindcss/postcss': {} } }
```
```css
/* app/globals.css */
@import "tailwindcss";

@theme {
  --color-brand: #F5B700;       /* Carolina yellow */
  --color-background: #FAF8F3;  /* warm cream */
  --radius-card: 14px;
}
```

**Requirements**: Node 20+, Safari 16.4+, Chrome 111+, Firefox 128+.

**Risk for comp110**: mockup.html uses CSS variables — Tailwind v4 `@theme` variables align well. DeepSeek Phase 2 can translate tokens directly from DESIGN_BRIEF §3 to `@theme` block.

---

## 2. TOEFL iBT Format — CRITICAL FINDING ⚠️

**ETS changed the iBT Reading format on January 21, 2026.**

### Old format (pre-Jan 2026) — what our app currently implements:
- 2 passages × 10 questions = 20 questions
- Long academic passages (~700 words), single-domain
- All question types: vocab, detail, inference, negative_fact, text_insertion, sentence_simplification, purpose, prose_summary

### New format (post-Jan 21, 2026) — what students actually face now:
- **Adaptive two-module structure**: routing module (10–12 min) determines difficulty tier
- **35–48 questions total** (down from 54 in full test)
- **Shorter passages** (~200 words), 5-question sets per passage
- **Broader content**: books, magazines, websites — not purely academic
- **Hard tier**: emphasizes academic vocabulary and inference
- **Easy tier**: emphasizes daily-life comprehension
- Navigation is within-module only (can't go back across modules)

### Impact on our TOEFL app:
| Dimension | Current App | New iBT |
|-----------|------------|---------|
| Passage length | ~700 words | ~200 words |
| Questions per passage | 9–10 | 5 |
| Question set size | 6 passages | Adaptive, shorter sets |
| Content type | Academic only | Mixed (academic/daily life) |
| prose_summary | Yes | Unclear — likely reduced or removed |

**Decision needed from user**:
1. **Keep old format** — explicitly position app as "legacy-format deep practice" (still useful for vocabulary/inference skill building)
2. **Add new short-passage mode** — implement 200-word passages with 5-question sets (new adaptive format)
3. **Hybrid** — keep existing 6 academic passages, add a new "Quick Practice" mode with shorter format

This is a master-gated decision. The current app is technically correct for the pre-Jan 2026 format but diverges from what test-takers face today.

---

## 3. AI Text Detection Data — RAID Benchmark

**RAID benchmark** (COLING 2025): Largest public challenge dataset
- 10M+ documents across **11 LLMs** (GPT-4, Claude, Gemini, Llama, Mistral, etc.)
- 11 genres, 4 decoding strategies, 12 adversarial attack types
- Hosted: `huggingface.co/datasets/liamdugan/raid`
- **Directly addresses ai-text-detector's gap**: current training data is DeepSeek-only; RAID covers GPT/Claude/Gemini

**Actionable path** (no API keys needed):
```bash
pip install datasets
python3 -c "
from datasets import load_dataset
ds = load_dataset('liamdugan/raid', split='train')
# Filter for AI-generated (label=1), sample by model family
gpt4 = ds.filter(lambda x: x['model'] == 'gpt-4')
claude = ds.filter(lambda x: 'claude' in x['model'])
"
```

This would let the user bootstrap multi-model training data from RAID without any API keys or new generation cost.

---

## Summary — Priority Actions

| Priority | Item | Effort | Blocker |
|----------|------|--------|---------|
| 🔴 HIGH | TOEFL format decision (old vs new) | ~4h for new format | User decision |
| 🟡 MED | comp110 Phase 2 Tailwind v4 setup note | Add to DESIGN_BRIEF | Can do now |
| 🟡 MED | ai-text-detector: RAID dataset path | ~1h script | Can do now |
| 🟢 LOW | Tailwind v4 upgrade guide in DESIGN_BRIEF | ~20 lines | Can do now |
