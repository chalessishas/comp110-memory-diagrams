# Writing Scorer Improvements Research

**Date:** 2026-04-12
**Current scorer:** 7 dimensions, weights: organization 33%, development 28%, vocabulary 14%, mechanics 10%, grammar 7%, relevance 5%, style 3%

## Key Findings from ETS Rubric Analysis

- **Score 5 vs Score 4 hinge on "unity, progression, coherence"** — not just having discourse markers, but having them form a logical chain. The current `organization.js` counts unique markers but does not detect whether they are used in a logically coherent sequence (e.g., "however" after a contrast, not after an agreement).
- **"Elaboration depth" is the single biggest differentiator** between score 3 and score 4-5. Thin ideas with correct grammar stay at 3. The current `development.js` uses word count ranges and "detail density" (noun/verb ratio), but does not penalize essays that are long but repetitive — the same claim restated 3 times in 300 words should not score the same as 3 distinct supporting points.
- **Syntactic range is underweighted** in the current scorer (style.js = 3%). ETS rubrics explicitly list "range of syntactic structures" as a score-5 requirement. The style module checks sentence length variance and 5 syntactic patterns — this is the right direction but at 3% weight has near-zero impact on the final score.
- **Argument completeness is missing entirely.** ETS scores assess whether the test-taker "fully addresses the task" — for an independent writing task this means: stated position + reason 1 with example + reason 2 with example + conclusion. The current relevance.js only checks keyword overlap with the prompt. There is no check for whether the essay contains a thesis statement and at least 2 developed reasons.
- **Tone/register detection is absent.** Score 3-4 essays fail on "inappropriate register" (too casual). The scorer has no casual language penalty. Phrases like "kinda", "stuff", "you know", "wanna" should subtract points.

## Source URLs

- https://www.ets.org/pdfs/toefl/toefl-ibt-writing-rubrics.pdf
- https://magoosh.com/toefl/toefl-sample-responses-and-how-to-grade-yourself/
- https://www.ets.org/toefl/test-takers/ibt/about/content/reading.html (for task context)
- https://www.bestmytest.com/blog/toefl/toefl-speaking-writing-score

## Recommendation

Three concrete improvements, estimated effort 2-4 hours total:

**1. Add argument structure check to `development.js` (highest ROI)**
Detect: does the essay have (a) a thesis/opinion statement, (b) at least 2 distinct supporting reasons, (c) at least 1 concrete example? Regex patterns for opinion markers + example markers (`for example`, `for instance`, `such as`, `one reason is`, `another reason`). Penalize essays >200 words that have 0-1 example markers — these are the "thin idea" essays that ETS caps at score 3.

**2. Raise `style.js` weight from 3% → 7%, reduce `mechanics.js` from 10% → 6%**
Spelling mechanics are a floor condition (serious errors tank the score), but for intermediate writers the bottleneck is syntactic range, not spelling. Rebalancing gives syntactic variety more signal. Recalibrate mechanics as a penalty rather than a positive score: start at 1.0 and subtract for each error type found.

**3. Add casual register penalty to `style.js`**
~15 high-frequency informal terms (`kinda`, `gonna`, `wanna`, `stuff`, `like,` as filler, `you know`, `cuz`, `btw`, `lol`). Each detected instance subtracts 0.05 from style score (capped at -0.3). This is a simple addition, ~10 lines of code, but captures a real ETS penalization category currently invisible to the scorer.
