# Research Loop — Session Status Report
**Date:** 2026-04-13 08:38:09  
**Researcher:** claude-sonnet-4-6 (automated research loop)  
**Task:** Review session state, codebase changes, incomplete tasks, and next improvement candidates.

---

## Current Engine State

| Metric | Value |
|--------|-------|
| Latest TOEFL commit | `55ff591` — Loop 28: make+adj without NP object |
| Calibration | 10/10 ✓ |
| 3→4 gap | +0.70 |
| 4→5 gap | +0.60 |
| grammar.js patterns | 60+ across 28 loops |

---

## Session Activity Summary (since midnight 2026-04-13)

The session has been extremely productive via autonomous loops:

| Loop | What was implemented |
|------|---------------------|
| 25 | progressive overuse penalty (style.js), have-difficulty+to-inf, prefer-X-than |
| 26 | besides sentence-initial penalty, reason-is-because, lacks-of, uncountable expansion (evidences/progresses/weathers), future-in-subordinate |
| 27 | modal+to-inf, despite+finite-clause, have+irregular past participle, is-lack-of, cope-to, formulaic bundle penalty (vocabulary.js) |
| 28 | as-far-as-I-concern idiom error, make+adj without NP object |

All calibration checks passed; no regressions.

---

## Incomplete / Pending Items

### 1. development.js P2 — Unsupported Degree-Adverb Claim Detector (DEFERRED)
- **Pattern**: Sentences using degree adverbs ("greatly", "significantly", "obviously", "extremely") without a causal connector ("because", "since", "as", "due to") in the same or next sentence
- **Rationale**: ETS rubric explicitly penalizes unwarranted generalizations; degree adverbs signal claims without evidence
- **Status**: Deferred since Loop 26 — requires threshold testing to avoid ~2% FP
- **Recommended approach**: Test on calibration set before deploying; only apply to essays ≥ 3 instances

### 2. Loop 29 — New Pattern Candidates (from research file `2026-04-13-research-loop-29.md`)

**Pattern 1: WISH_INDICATIVE_RE** ★★★ HIGHEST PRIORITY
```js
const WISH_INDICATIVE_RE = /\bwish(?:es)?\s+(?:I|he|she|they|we|you|it)\s+(can|will|am|is|are|have|has|do|does|may|shall)\b/gi
```
- **Error**: "I wish I can improve my skills." (should: "I wish I could")
- **FP rate**: ~1-3% (near-zero for listed auxiliaries)
- **Frequency**: ~6-8% of Chinese L1 TOEFL essays  
- **QWK est.**: +0.012–0.018
- **Evidence**: 71% of Chinese EFL learners use wish+present (Atlantis Press 2021); CLEC top-5 verb phrase error (Liu 2014)

**Pattern 2: MODAL_ING_EXTRA_RE** ★★ HIGH PRIORITY
```js
const MODAL_ING_EXTRA_RE = /\b(must|shall|need to|ought to|have to|used to)\s+(\w+ing)\b(?!\s+(?:to|be|have))/gi
```
- **Gap**: Loop 19 covers can/could/would/should/will/may/might — this fills must/shall/need to/ought to/have to
- **Error**: "Students must considering multiple factors."
- **FP rate**: ~2-4%
- **Frequency**: ~4-6% Chinese L1 TOEFL essays
- **QWK est.**: +0.008–0.012

**Pattern 3: SUBORD_BARE_3SG_RE** ★★★ HIGHEST QWK POTENTIAL
```js
const SUBORD_BARE_3SG_RE = /\b(although|though|even though|because|since|when|whenever|while|if|unless|after|before|as|once|whereas|provided)\s+(?:it|he|she)\s+(go|come|show|provide|improve|develop|...)\b(?!s\b|ing\b|ed\b|'s\b)/gi
```
- **Error**: "Although technology improve our lives…" (subordinate clause 3rd-sg -s drop)
- **Gap vs Loop 6**: Loop 6 catches main-clause 3rd-sg omission; this catches subordinate clause position where frequency is 2x higher for advanced learners
- **FP rate**: ~3-5%
- **Frequency**: ~7-9% Chinese L1 TOEFL essays
- **QWK est.**: +0.015–0.022 — **highest estimated gain of any Loop 29 candidate**

---

## Implementation Recommendation

**Implement in this order for Loop 29:**

1. **WISH_INDICATIVE_RE** first — cleanest pattern, near-zero FP, high frequency
2. **MODAL_ING_EXTRA_RE** second — gap-fill for Loop 19, trivial to implement alongside Pattern 1
3. **SUBORD_BARE_3SG_RE** third — highest ROI but requires more careful regex (long verb list)

**Skip for now:**
- Pattern 4 (NO_MATTER calque) — "No matter what benefits it brings" is grammatically valid in English, making FP boundaries complex
- development.js P2 — still needs threshold testing in a dedicated active session

**Combined estimated QWK gain (Patterns 1-3)**: +0.035–0.052

---

## No User-Blocking Items Identified

All active tasks are proceeding autonomously. No passwords, API keys, design decisions, or external service outages detected. System is GREEN.
