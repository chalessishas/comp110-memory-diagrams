# Loop 45 Strategy: Pivot to Organization.js

**Date**: 2026-04-13 23:03  
**Trigger**: Progress Loop sub-agent discussion (2 agents)

## Sub-Agent Findings Summary

### Agent 1: Diminishing Returns Analysis
Grammar is at 112 patterns and 7% weight. Each new pattern covers ≤0.5% of essays.
Expected QWK gain per pattern: +0.001–0.003.

Recommended pivot order (highest ROI first):
| Action | Module | Weight | Effort | Expected QWK |
|--------|--------|--------|--------|-------------|
| Semantic precision | vocabulary.js | 14% | 4–5 hrs | +0.08–0.12 |
| Argument completeness | development.js | 28% | 6–8 hrs | +0.10–0.15 |
| Cross-paragraph coherence | organization.js | 33% | 5–7 hrs | +0.07–0.10 |
| Clause-type inventory | style.js | 7% | 6–7 hrs | +0.05–0.08 |
| Grammar #113+ | grammar.js | 7% | 10–15 hrs | +0.005–0.010 |

### Agent 2: Grammar Candidates (Loop 45 backup)
5 candidates identified, but mixed quality:
1. Zero article generic mass nouns — Medium FP
2. Simple past/present tense swap — Medium FP, tricky
3. Overdeterminer with ordinals — **High FP, skip**
4. Modal + progressive infinitive — Low FP, but overlaps existing patterns
5. Article before proper nouns ("The Zhang thinks") — Low FP, clean

## Score Breakdown Analysis (current baseline)

```
            S3      S4      S5
grammar     1.00    1.00    1.00
mechanics   1.00    1.00    1.00
vocabulary  —       1.00    1.00
organization —      0.87    0.97   ← 0.10 gap (widening this = highest ROI)
development —       0.73    1.00   ← already maxed for S5
style       —       0.63    0.81   ← 0.18 gap
relevance   —       0.70    0.70

Overall:    3.50    4.20    4.80
```

**Key finding**: development.js is saturated (S5 = 1.00). New development bonuses have zero marginal effect. The organization gap (0.87 vs 0.97 = only 0.10) is the bottleneck.

## Proposed Loop 45: Organization Improvements

### P1 — Conclusion Quality Detection (organization.js)
**What**: Does the final paragraph restate the thesis or reference intro keywords?

ETS Score-5 rubric: "conclusion should revisit the thesis, not introduce new ideas."
Chinese L1 weakness: trailing "In conclusion, I think X is good" without connecting back.

Implementation:
- Extract top 3 content keywords from first paragraph (intro)
- Check if last paragraph contains ≥1 of those keywords
- Bonus: +0.04 (partial restatement) / +0.08 (clear restatement)
- Guard: skip essays < 100 words or < 2 paragraphs

Expected FP: ~5% (some valid conclusions introduce synthesis, not direct restatement)
Estimated QWK: +0.03–0.06

### P2 — Macro-Structure Completeness (organization.js)  
**What**: Detect intro / body / conclusion structure beyond just marker presence.

Current scorer: counts discourse markers (7 categories). Doesn't check paragraph-level function.
Score-5 essays: intro paragraph ends with thesis statement → body paragraphs develop → conclusion paragraph wraps up.

Implementation:
- Paragraph count ≥ 3 → structural signal
- Intro: contains thesis markers (already have THESIS_MARKERS)
- Conclusion: contains conclusion markers ("in conclusion", "in summary", "overall", "to sum up")
- Bonus: +0.05 for complete 3-part structure; +0.03 for partial (intro + conclusion, no body)
- Guard: discussion and general only, ≥100 words

Expected FP: ~3% 
Estimated QWK: +0.04–0.07

### P3 — Topic Sentence Cohesion (organization.js)
**What**: Each body paragraph's first sentence should connect to the essay-level argument.

Heuristic: first sentence of each body paragraph contains at least 1 content keyword from the essay title/prompt or a transition marker that links to prior paragraph.

This is hard to implement well without prompt text. **Defer until prompt text is reliably passed.**

## Recommended Implementation Order

1. **P2 first** (macro-structure) — safest, lowest FP, directly targets 4→5 gap
2. **P1 second** (conclusion quality) — moderate complexity, clear signal
3. **Grammar Agent 2 Candidate 5** (article before proper nouns) — if still needed after P1+P2

## Calibration Risk Assessment

- S4 essay (single paragraph) → P2: 0 bonus (< 3 paragraphs) → safe
- S5 essay (2 paragraphs) → P2: partial bonus (+0.03) → safe
- After P1+P2: S5 organization 0.97→1.00, S4 stays 0.87 → gap widens to 0.13

## Stop Condition for Grammar Loop

Recommend stopping grammar pattern additions at Loop 44 (112 patterns) unless:
- A clear high-frequency error type is identified that is NOT similar to existing patterns
- FP risk is < 2%
- The pattern is from a peer-reviewed CLEC/BEA source published after 2020
