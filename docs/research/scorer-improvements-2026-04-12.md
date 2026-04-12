# Writing Scorer Improvements — Research 2026-04-12
**Scope:** Pure-JS e-rater approximation in `TOEFL/src/writing/scorer/`  
**Current weights:** grammar 7%, mechanics 6%, vocabulary 14%, organization 33%, development 28%, style 7%, relevance 5%  
**Research date:** 2026-04-12  

---

## Query 1 — ETS e-rater Macrofeatures & Actual Weights

### Source 1
- **URL:** https://www.ets.org/erater/how.html
- **Key finding:** e-rater v13.1 uses 10 macrofeatures in a linear regression: organization, development, grammar, usage, mechanics, style, word length, word choice, collocation & preposition, and sentence variety. Weights are not fixed constants — they are determined empirically per-prompt by regressing human scores against feature values. "Generic models" pool related prompts; "prompt-specific models" tune per-question.
- **Actionable improvement:** Our scorer conflates "usage" (agreement, verb tense, article correctness) with "grammar" (structural fragment/run-on detection). These are separate macrofeatures in e-rater. Splitting grammar.js into grammar (structural) + usage (morphosyntactic) and adding even simple article/tense error detection would better mirror real e-rater coverage.

### Source 2
- **URL:** https://files.eric.ed.gov/fulltext/EJ1168485.pdf (Chen et al., 2017 — ETS Research Report)
- **Key finding:** Grammar, Usage, Mechanics, and Style are composed of *microfeatures* that are currently equally weighted within each macrofeature group. The paper proposes empirical weighting where microfeatures more predictive of human scores receive higher weight, yielding modest but consistent improvement. The equal-weight default remains the production baseline.
- **Actionable improvement:** Within our grammar.js, run-on sentences are far more diagnostic than double negation (double negation is rare; run-ons are pervasive in ESL writing). Consider weighting the run-on penalty 3× the fragment/double-negation penalty rather than treating all grammar error types equally.

### Source 3
- **URL:** https://www.ets.org/pdfs/e-rater/automated-essay-writing-e-rater-iaea-paper.pdf
- **Key finding:** Organization in e-rater is operationalized as counts of discourse element types: thesis statement, main point, supporting idea, conclusion, and transition. Supporting ideas are only credited when immediately following a main point. Paragraphing is a secondary signal.
- **Actionable improvement:** Our organization.js scores discourse markers (additive connectors, contrast markers, etc.) but does NOT distinguish their positional role. A "therefore" in the opening sentence and one closing an argument body paragraph are structurally different. Adding a simplistic positional model — intro paragraph thesis-like sentence, body paragraphs with topic sentences, closing paragraph — would better approximate e-rater's discourse element model.

### Source 4
- **URL:** https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12094 (Chen 2016 — Machine Learning Scoring Models)
- **Key finding:** Modern e-rater builds scoring models using both linear regression and ensemble ML methods. The feature set includes "sentence variety" as a distinct macrofeature separate from style — measured as frequency of different syntactic constructions (simple, compound, complex, compound-complex).
- **Actionable improvement:** Our style.js currently measures sentence length variance as a proxy for syntactic variety. Sentence length variance and syntactic variety are correlated but not the same — a student can write sentences of varied length all in simple SVO form. Adding a dedicated syntactic-type classifier (pattern detection: subordinating conjunctions → complex, coordinating conjunctions between two independent clauses → compound, relative pronouns → complex) would split these two macrofeatures properly.

---

## Query 2 — TOEFL Writing Score 4 vs Score 5: Specific Distinctions

### Source 5
- **URL:** https://www.ets.org/pdfs/toefl/toefl-ibt-writing-rubrics.pdf (Official ETS Rubric)
- **Key finding (Integrated Writing):**
  - Score 5: "Selects the relevant information from the lecture and coherently and accurately presents this information in relation to the relevant information presented in the reading. The response is well organized, and occasional language errors that are present do not result in inaccurate or imprecise presentation of content or connections."
  - Score 4: "Generally good in selecting relevant and important information and in coherently and accurately relating the relevant parts of the lecture to information given in the reading, but may have minor omission, inaccuracy, imprecision, or vagueness in some of what is presented."
  - **The score 4/5 boundary is almost entirely about information accuracy and completeness, not language quality.** Language errors are tolerated at score 5 if they don't distort meaning.
- **Actionable improvement:** For the Integrated Writing task (if we ever add it), content accuracy detection requires knowing the source lecture/reading. Our current scorer cannot assess this. For Independent Writing, the distinction maps more cleanly to language facility. This finding is less actionable for our current task types (email + discussion).

### Source 6
- **URL:** https://www.ets.org/pdfs/toefl/writing-rubrics.pdf (Official ETS Write an Email Rubric)
- **Key finding:**
  - Score 5: "successfully accomplishes all three communicative goals," "precise, idiomatic word choice," "variety of syntactic structures," "almost no lexical or grammatical errors other than those expected of a competent writer."
  - Score 4: "accomplishes all three communicative goals with some lapses in precision or clarity," "minor errors in structure, word form, or use of idiomatic language," "occasional redundancy or digression."
  - **Three communicative goals** = the three bullet points in the email prompt (e.g., "explain your situation / make a request / suggest a time"). A score 4 essay addresses all three but with reduced precision.
- **Actionable improvement:** Our development.js measures word count and "detail density" but has no concept of communicative goal completeness. A response that addresses only 2 of the 3 prompt bullet points should score lower than one that hits all 3. We could implement this by extracting prompt bullet points (split on `\n-` or `•` or numbered lists) and checking keyword overlap for each individually rather than treating the whole prompt as one relevance query. This is a significant accuracy improvement for the email task.

### Source 7
- **URL:** https://www.writing30.com/blog/toefl-writing-rubrics
- **Key finding:** Practical breakdown confirms that score 5 requires *consistent* precision throughout the essay, not just occasional high-quality sentences. Score 4 writers "usually get it right but have inconsistent stretches." Raters evaluate holistically — a strong opening followed by a weak conclusion can pull a score down from 5 to 4.
- **Actionable improvement:** Our scorer evaluates distributions (TTR, avg sentence length) but not consistency across the essay. Adding a "consistency penalty" — e.g., penalizing if the last third of the essay shows significantly lower vocabulary diversity than the first two-thirds — would capture this holistic consistency signal. Low implementation cost: split essay into thirds by word count, compute TTR per segment, penalize if final-third TTR drops >20% below overall TTR.

---

## Query 3 — Academic Discourse Markers: Gaps in Current Scorer

### Source 8
- **URL:** https://ccsenet.org/journal/index.php/ijel/article/download/0/0/51434/55882 (Corpus-Based Analysis of Discourse Markers in ESL)
- **Key finding:** Proficient ESL writers use significantly more *inferential* markers (therefore, thus, consequently, hence) and *concessive* markers (although, while, despite, nevertheless) than lower-proficiency writers, who over-rely on *additive* markers (also, and, furthermore, moreover). The ratio of inferential+concessive to additive markers correlates with writing quality.
- **Actionable improvement:** Our organization.js treats all discourse markers equally in a flat count. Categorize markers by type and compute the inferential/concessive vs additive ratio. A high ratio → higher organization score. This is a direct quality signal, not just a fluency signal.

### Source 9
- **URL:** https://wisc.pb.unizin.org/esl117/chapter/chart-of-transition-signals/ (University of Wisconsin ESL Writing Guide)
- **Key finding:** Complete categorization of academic transitions:
  - **Additive:** furthermore, moreover, in addition, additionally, also, besides, equally important
  - **Contrast/Concessive:** however, nevertheless, on the other hand, conversely, in contrast, despite, although, even though, while, whereas, yet
  - **Causal:** therefore, thus, consequently, as a result, hence, for this reason, since, because
  - **Exemplification:** for example, for instance, specifically, namely, in particular, to illustrate
  - **Emphasis:** indeed, in fact, certainly, above all, most importantly
  - **Sequence:** first, second, then, subsequently, finally, next, last, previously
  - **Summary/Restatement:** in conclusion, in summary, to summarize, in other words, that is, in short, overall
- **Actionable improvement (concrete):** Cross-reference our current organization.js marker list against this taxonomy. Specific gaps to check: "whereas," "conversely," "to illustrate," "namely," "hence," "above all," "subsequently," "in short." Add these. More importantly — implement the three-tier categorization (additive / contrast+causal / exemplification+emphasis) and reward category *diversity* rather than raw count.

### Source 10
- **URL:** https://www.numberanalytics.com/blog/mastering-discourse-markers-in-academic-writing
- **Key finding:** Hedging language (it could be argued, one might suggest, this may indicate) and boosters (it is clear that, undoubtedly, certainly) are distinct discourse marker categories important in academic writing. Hedging signals epistemic awareness; ETS rubrics at score 5 expect mature stance-taking, not just connective fluency.
- **Actionable improvement:** Add a "stance marker" sub-score to vocabulary.js or style.js. Detect hedges (may, might, could, it is possible, arguably, it seems, tends to) and boosters (clearly, obviously, undoubtedly, it is evident). Neither overusing nor underusing these is ideal — target range for academic writing is ~2-4 hedge phrases per 150 words. Penalize complete absence (unsophisticated) and overuse (hedges every claim, appears uncertain).

---

## Query 4 — Common Grammar/Style Errors in TOEFL Writing

### Source 11
- **URL:** https://professorscottsenglish.com/english-grammar/common-grammar-mistakes/what-are-common-grammar-mistakes/what-are-common-grammar-mistakes-in-toefl-writing-responses/
- **Key finding:** Top 5 most frequent TOEFL writing grammar errors (ranked by rater impact):
  1. **Subject-verb agreement** — especially across prepositional phrases ("The group of students *are*...")
  2. **Article misuse** — missing "the" for definite reference, wrong article before vowel sounds
  3. **Run-on sentences** — two independent clauses joined by comma only (comma splice)
  4. **Preposition errors** — wrong prepositions in fixed phrases ("interested *on*" vs "interested *in*")
  5. **Incorrect verb tense consistency** — mixing present/past within the same argument
- **Actionable improvement:** Our grammar.js currently catches run-ons and comma splices (good), but has zero coverage for subject-verb agreement, article errors, preposition errors, or tense consistency. These are the actual high-frequency errors raters penalize. Adding even heuristic checks for the most common SVA patterns (plural noun before singular verb, "there is" + plural noun) would improve the grammar score's correlation with human rater judgments.

### Source 12
- **URL:** https://magoosh.com/toefl/toefl-grammar-mistake-run-on-sentences/
- **Key finding:** Run-on sentences in TOEFL writing are one of the most penalized errors because they signal low grammatical control, not just a surface mistake. A single run-on in an otherwise strong essay can pull a score from 5 to 4. The fix is structural (add period, semicolon, coordinating conjunction, or subordinator) — not cosmetic.
- **Actionable improvement:** Our current run-on detection already flags this, but the penalty weight may be too low. Consider increasing the run-on penalty relative to other grammar errors. Each detected run-on could apply a 0.15 deduction (currently unclear what the per-error deduction is in grammar.js).

### Source 13
- **URL:** https://edubenchmark.com/blog/subject-verb-agreement-and-the-toefl/ (Benchmark Education)
- **Key finding:** SVA errors are particularly common in three patterns: (a) collective nouns ("The committee *are*"), (b) indefinite pronouns ("Everyone *are*"), (c) inversion after "there" ("There *was* many problems"). These are the hardest for intermediate ESL writers because translation interference from L1 is strong.
- **Actionable improvement:** Add three specific SVA regex patterns to grammar.js:
  - `/(everyone|someone|anyone|nobody|nothing)\s+(are|were)\b/i`
  - `/\bthere\s+were?\s+\w+\s+(reason|problem|issue|way|time)s\b/i` (inverted SVA)
  - Pattern is limited but catches the most common ESL-specific errors without requiring a full parser.

### Source 14
- **URL:** https://college-council.com/en/blog/toefl-2026-writing-new-tasks-guide
- **Key finding:** As of the 2025/2026 TOEFL format update, the independent essay ("agree/disagree") is gone, replaced by three shorter tasks. The two active scored tasks remain Write an Email and Academic Discussion. Style errors that were penalized in independent essays (e.g., overusing "I believe," "In my opinion") are now less relevant — the Academic Discussion task actually *expects* first-person opinion expression and explicitly graded engagement.
- **Actionable improvement:** Our style.js currently applies a "casual penalty" for phrases like "I think," "I believe," "in my opinion." This was calibrated for the old independent essay format. For the Academic Discussion task, these phrases are *appropriate* and expected. The casual penalty should be zeroed or reduced to near-zero when `taskType === 'discussion'`. This is a correctness bug, not just a tuning issue.

---

## Summary: Highest-Impact Actionable Improvements

| Priority | Module | Change | Complexity | Why |
|----------|--------|--------|------------|-----|
| 1 | style.js | Remove casual penalty for discussion task (`taskType === 'discussion'`) | XS — 2 lines | Correctness bug: "I believe" is required by ETS rubric for discussion |
| 2 | organization.js | Categorize markers into tiers (additive / concessive+causal / exemplification) and reward diversity | S — 30 lines | Corpus research shows tier diversity correlates with quality; flat count does not |
| 3 | grammar.js | Add 3 SVA regex patterns (everyone/are, there was + plural, indefinite pronoun + plural verb) | S — 15 lines | SVA is the #1 human-rater grammar signal, currently undetected |
| 4 | relevance.js | Split prompt bullet points and check each separately instead of whole-prompt overlap | M — 50 lines | Score 4→5 boundary for email task is communicative goal completeness per-bullet |
| 5 | organization.js | Add positional discourse model: detect intro/body/conclusion paragraphs and reward thesis+topic-sentences pattern | M — 40 lines | Mirrors actual e-rater organization macrofeature which is positional, not just marker density |
| 6 | style.js | Add "consistency" penalty — TTR drop in final essay third vs overall | S — 20 lines | Score 4 vs 5 distinction is consistent precision throughout, not just peak quality |

---

## Sources

- [ETS How e-rater Works](https://www.ets.org/erater/how.html)
- [Chen et al. 2017 — e-rater Grammar/Usage/Mechanics/Style Microfeatures](https://files.eric.ed.gov/fulltext/EJ1168485.pdf)
- [Chen 2016 — Machine Learning Scoring Models for e-rater](https://onlinelibrary.wiley.com/doi/full/10.1002/ets2.12094)
- [ETS TOEFL iBT Integrated Writing Rubric](https://www.ets.org/pdfs/toefl/toefl-ibt-writing-rubrics.pdf)
- [ETS Write an Email Writing Rubric](https://www.ets.org/pdfs/toefl/writing-rubrics.pdf)
- [TOEFL Writing Rubrics 2026 — Writing30](https://www.writing30.com/blog/toefl-writing-rubrics)
- [Corpus-Based Analysis of Discourse Markers in ESL — CCSE](https://ccsenet.org/journal/index.php/ijel/article/download/0/0/51434/55882)
- [Transition Words Chart — UW ESL Writing](https://wisc.pb.unizin.org/esl117/chapter/chart-of-transition-signals/)
- [Mastering Discourse Markers in Academic Writing — NumberAnalytics](https://www.numberanalytics.com/blog/mastering-discourse-markers-in-academic-writing)
- [Common Grammar Mistakes in TOEFL Writing — Professor Scott's English](https://professorscottsenglish.com/english-grammar/common-grammar-mistakes/what-are-common-grammar-mistakes/what-are-common-grammar-mistakes-in-toefl-writing-responses/)
- [TOEFL Grammar Mistake: Run-On Sentences — Magoosh](https://magoosh.com/toefl/toefl-grammar-mistake-run-on-sentences/)
- [Subject-Verb Agreement and the TOEFL — Benchmark Education](https://edubenchmark.com/blog/subject-verb-agreement-and-the-toefl/)
- [TOEFL 2026 Writing New Tasks Guide — College Council](https://college-council.com/en/blog/toefl-2026-writing-new-tasks-guide)
