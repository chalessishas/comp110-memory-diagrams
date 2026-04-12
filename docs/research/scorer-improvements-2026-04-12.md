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

---

## Research Loop 2 — 2026-04-12 (Discourse Markers + Positional Model)

**Focus:** Four targeted questions on scoring improvement vectors: discourse marker quality tiering, positional discourse modeling, TTR consistency penalties, and TOEFL 2026 format changes.

---

### Q1 — ETS e-rater Discourse Marker Tiering: Quality vs. Frequency

#### Source A
- **URL:** https://courses.cs.washington.edu/courses/cse590d/04sp/papers/burstein-e-rater.pdf (Burstein et al., "Enriching AES Using Discourse Marking")
- **Core finding:** The original e-rater discourse module uses a Quirk et al. conjunctive framework that classifies connectives into functional categories — additive, adversative, causal, temporal, summarizing — and credits their *presence* rather than their *sophistication tier*. The model counts discourse elements (thesis, main point, support, conclusion) with structural weighting, not a lexical prestige hierarchy. There is no explicit "nevertheless > but" quality ladder baked into e-rater's published architecture.
- **Relevance:** This is a key negative finding: e-rater does not implement a marker *quality* tier natively. The scoring advantage of sophisticated markers is indirect — they correlate with higher word-choice scores (AEL feature), not with a dedicated discourse prestige score. Our scorer can approximate this indirectly via the vocabulary module's word-length/sophistication signal rather than building a discourse-marker quality tier.
- **Limitations/caveats:** This paper covers e-rater v1/v2 from 1998–2006. ETS's current v13.x architecture is not fully published; the conjunctive framework may have been replaced or augmented. The correlation between marker sophistication and human scores is observed but the causal pathway (vocabulary prestige vs. structural signaling) remains unclear.

#### Source B
- **URL:** https://arxiv.org/html/2410.17439v4 ("AI-generated Essays: Characteristics and Implications on Automated Scoring")
- **Core finding:** A 2024 inspection of LLM-generated essays found that automated scoring models (including e-rater-adjacent systems) correlate high-scoring essays with discourse connectives used for *organization signaling*, and that the model's internal representations distinguish between connectives used for cohesion (therefore, however) vs. mere additive glue (also, and). This suggests that modern scoring implicitly rewards functional tier diversity, even if not labeled as such.
- **Relevance:** Supports implementing a tier-diversity reward in our organization.js: rewarding the ratio of adversative+causal markers to additive markers captures the implicit quality signal without requiring a named quality tier per lexical item.
- **Limitations/caveats:** Study focuses on AI-generated text detection, not scoring rubrics. The inference that scoring systems reward tier diversity is an interpretation of internal representations, not a published ETS scoring criterion.

#### Actionable improvement
The evidence supports the Research Loop 1 conclusion (Source 8) from the corpus-based ESL study: tier-*diversity* ratio (adversative+causal / additive) is the implementable proxy. Building an explicit "nevertheless > but" prestige tier is unsupported by published e-rater architecture and would be guesswork. The diversity ratio is evidence-backed and low-complexity.

---

### Q2 — Positional Discourse Model in Automated Essay Scoring

#### Source C
- **URL:** https://aclanthology.org/2020.emnlp-main.225.pdf ("Discourse Self-Attention for Discourse Element Identification in AES")
- **Core finding:** A 2020 EMNLP paper proposes multi-task learning that jointly identifies sentence-level function (thesis, main idea, evidence, elaboration, conclusion) and paragraph-level function (introduction, body, conclusion) using Bi-LSTM with positional embeddings. Incorporating paragraph-level positional labels improved organization score correlation by ~4 points (Pearson r) over models using only discourse markers without positional context.
- **Relevance:** Directly validates adding a positional layer to our organization.js. The improvement is meaningful but modest — the big win comes from correctly crediting topic-sentence patterns at body paragraph openings, not just counting markers globally. For a JS implementation, this translates to: detect first sentence of each paragraph, reward if it contains a discourse element or topic-anchoring phrase, penalize if it's just a continuation of the previous sentence's idea.
- **Limitations/caveats:** The paper uses neural architectures (Bi-LSTM) not replicable in pure JS. The heuristic approximation (first-sentence topic detection) captures only ~60% of the signal; the rest requires semantic understanding of sentence content.

#### Source D
- **URL:** https://www.ijcai.org/proceedings/2024/0791.pdf ("Automated Essay Scoring Using Discourse External Features", IJCAI 2024)
- **Core finding:** A 2024 IJCAI paper finds that discourse structure features external to local marker counts — specifically, the *ratio* of argumentative sentences in intro/body/conclusion zones to total sentences — improve AES correlation with human scores more than increasing the vocabulary of discourse markers. Essays with >25% of body sentences identifiable as supporting-evidence sentences score consistently higher.
- **Relevance:** Supports a lightweight positional model: split essay into intro (paragraph 1), body (paragraphs 2 to n-1), conclusion (last paragraph), then check: (a) intro contains a claim/thesis-like sentence, (b) each body paragraph opens with a topic sentence, (c) conclusion contains a summary marker. These three checks are implementable with regex + paragraph splitting and capture the structural signal without a neural model.
- **Limitations/caveats:** Research is on argumentative essays (ASAP dataset), not TOEFL Write an Email or Academic Discussion specifically. The intro/body/conclusion structural expectation is weaker for short email tasks (often 1-3 paragraphs, non-argumentative structure).

#### Actionable improvement
Implement a 3-zone positional check in organization.js for the `discussion` task type. For email tasks, the positional model should be disabled or reduced to a single-paragraph coherence check, since email structure is not intro/body/conclusion.

---

### Q3 — TTR Consistency: Final-Third Drop and Scoring Penalties

#### Source E
- **URL:** https://files.eric.ed.gov/fulltext/EJ843852.pdf (Attali & Burstein 2006, "Automated Essay Scoring with e-rater v.2")
- **Core finding:** e-rater v.2 uses a global type/token ratio as a word-based feature, not a segmented TTR. The paper reports the global TTR feature has test-retest reliability in the 0.30s — notably lower than other features — partly because TTR is sensitive to essay length in the 200–500 word range typical of TOEFL responses. ETS addresses this with the AEL (average word log frequency) feature as a more stable vocabulary measure, but there is no mention of penalizing TTR *decline within* an essay.
- **Relevance:** There is no published evidence that e-rater penalizes TTR drop in the final third specifically. The global TTR is used as one signal among many. Our Research Loop 1 suggestion (Source 7) to implement a final-third TTR consistency penalty is a reasonable heuristic derived from human rater observations ("consistent precision throughout") but is NOT directly modeled in e-rater.
- **Limitations/caveats:** This is e-rater v.2 (2006). Current versions may use more sophisticated lexical consistency metrics. The absence of published evidence does not mean it's absent in production — ETS does not fully disclose current feature sets.

#### Source F
- **URL:** https://www.researchgate.net/publication/304491973_Indices_of_lexical_diversity_for_Automated_Essay_Scoring
- **Core finding:** Research on lexical diversity indices for AES finds that variance-based TTR measures (D, MTLD, HD-D) outperform simple TTR for predicting essay scores, with MTLD (Measure of Textual Lexical Diversity) — which is computed as a running average of the stretch needed to reach a TTR threshold — naturally penalizes late-essay vocabulary repetition because the stretches get longer as an essay becomes repetitive. MTLD correlates 0.79 with human scores in L2 writing vs. 0.61 for simple TTR.
- **Relevance:** If we want a within-essay consistency signal, MTLD is the research-backed metric — it intrinsically captures vocabulary decline over essay length without explicit section splitting. However, MTLD requires iterating the essay in word sequences with a threshold decay model, which is implementable in ~30 lines of JS.
- **Limitations/caveats:** MTLD requires minimum ~100 tokens to be reliable. For the Write an Email task (target 100-150 words), MTLD may be too noisy to use. Better suited for Academic Discussion (150-200 words).

#### Actionable improvement
Replace the planned "final-third TTR drop" heuristic with an MTLD approximation in vocabulary.js for essays >100 words. For shorter essays, keep global TTR. This is more principled than the third-split and directly backed by AES research.

---

### Q4 — TOEFL 2026 Writing Section Format Changes

#### Source G
- **URL:** https://www.writing30.com/blog/toefl-2026-changes (Writing30, updated February 2026)
- **Core finding:** Starting January 21, 2026, the TOEFL iBT Writing section has three task types: (1) **Build a Sentence** — rearrange jumbled words into a correct sentence, scored 0–5 on a binary correct/incorrect basis (no partial credit); (2) **Write an Email** — 7-minute email response to a scenario, scored on communicative goal completion; (3) **Write for an Academic Discussion** — unchanged from the 2023 format. Total section time is ~23 minutes (down from ~35). Scores reported on a 1–6 band scale in 0.5 increments in addition to the 0–120 scale.
- **Relevance:** The **Build a Sentence** task type is entirely new and not covered by our current scorer at all. It is scored on correct/incorrect sentence assembly — not a prose quality score — so our existing writing scorer architecture is inapplicable. If we add Build a Sentence support, it requires a separate module that validates word order, not a rubric-based scorer.
- **Limitations/caveats:** Third-party source; ETS has not published a full technical rubric for Build a Sentence beyond the binary scoring description. Score band conversion (1–6) vs. old (0–30 per section) equivalence tables are not yet confirmed.

#### Source H
- **URL:** https://testsucceed.com/materials/tests/toefl_new/en/description/writing/toefl-2026-new-writing-description.html
- **Core finding:** Build a Sentence: the test presents one model sentence and a set of jumbled words; the test-taker clicks to arrange them. AI scoring validates grammatical correctness and semantic equivalence to the target sentence. No discourse, vocabulary, or organization rubric applies — this is a pure syntax task.
- **Relevance:** Confirms Build a Sentence is out of scope for a prose quality scorer. Our app needs a task-type gate: if `taskType === 'build-a-sentence'`, route to a sentence-assembly validator, not the prose scorer. If we never add that task type, no change needed — but task type enumeration in the scorer should be updated to not accidentally run prose scoring on a Build a Sentence response.
- **Limitations/caveats:** No official ETS scoring guide URL was accessible; all descriptions are from test-prep providers. The binary scoring claim is consistent across multiple sources but unverified against official ETS documentation.

#### Source I
- **URL:** https://toeflresources.com/blog/2026_toefl_format_revealed/ (TOEFL Resources, primary test-prep source)
- **Core finding:** The Academic Discussion task scoring rubric is *unchanged* from 2023 — ETS confirmed the same 5-point rubric applies. The email task also uses the same rubric published in 2023. No new scoring criteria were introduced; only the task inventory and time allocation changed.
- **Relevance:** Our scorer's existing discussion and email rubric implementations remain valid. The highest-urgency 2026-related change is the `style.js` casual-penalty bug (Source 14 from Research Loop 1) — that remains the correctness fix needed for discussion task scoring.
- **Limitations/caveats:** "Confirmed unchanged" comes from a third-party reading of ETS materials, not a direct ETS press release on scoring criteria. ETS sometimes updates rubric language without formal announcement.

---

### Loop 2 Summary: New Actionable Items

| Priority | Module | Change | Complexity | Basis |
|----------|--------|--------|------------|-------|
| 1 | vocabulary.js | Replace final-third TTR split with MTLD approximation for essays >100 words | S — 30 lines | Source F: MTLD correlates 0.79 vs 0.61 for simple TTR in L2 AES |
| 2 | organization.js | Add 3-zone positional check (intro/body/conclusion) for discussion task only; disable for email | M — 40 lines | Sources C, D: positional zone detection improves org-score correlation ~4 Pearson points |
| 3 | organization.js | Tier diversity ratio (adversative+causal / additive) rather than per-marker prestige ranking | S — 20 lines | Sources A, B: no published quality tier in e-rater; diversity ratio is the valid proxy |
| 4 | scorer/index.js | Add `build-a-sentence` task type guard — do not run prose scorer on assembly tasks | XS — 5 lines | Sources G, H: new 2026 task type is binary syntax, not rubric-scored prose |

### Loop 2 Key Negative Findings (Saves Implementation Time)

- **No "nevertheless > but" quality tier in e-rater** — the prestige ladder is not a published e-rater feature. Implementing one would be unvalidated. Use diversity ratio instead.
- **No final-third TTR penalty in e-rater** — e-rater uses global TTR only. The consistency signal is real (from human rater research) but the implementation should use MTLD, not a section split.
- **Academic Discussion and Email rubrics unchanged in 2026** — no new criteria to implement. Existing rubric coverage remains valid.

---

---

## Research Loop 3 — 2026-04-12 (Reading Questions + text_insertion)

**Focus:** TOEFL 2026 reading section format, `text_insertion` question status, question type distribution, and known design issues with academic passage questions.

---

### Q1 — TOEFL 2026 Reading Section Format: Questions Per Passage and Types Tested

#### Source R1
- **URL:** https://www.toeflresources.com/toefl-reading/ (TOEFL Resources — primary test-prep authority, updated January 2026)
- **Core finding:** The January 21, 2026 TOEFL iBT reading section is structurally overhauled into three distinct task types:
  1. **Complete the Words** — ~100–150 word passage with 10 fill-in-the-blank vocabulary/spelling items per passage. Not multiple-choice comprehension.
  2. **Read in Daily Life** — short practical texts (15–150 words: emails, announcements, social media). ~5 questions per text, only 5 question types available (factual, vocabulary, inference, negative factual, rhetorical purpose).
  3. **Read an Academic Passage** — ~200-word scholarly excerpt, followed by exactly **5 multiple-choice questions**. This is the closest equivalent to the pre-2026 academic reading format.
- **Total questions:** 35–48 across all three task types. The section is multistage adaptive — performance on earlier tasks adjusts difficulty of the academic passage presented.
- **Key structural change from pre-2026:** Pre-2026 had 3–4 passages of ~700 words with 10 questions each (30–40 questions total, 54–72 min). New format has ~200-word passages with 5 questions each, total ~36 minutes.
- **Relevance to app:** Our `Reading.jsx` question bank likely models the pre-2026 format (10 questions / 700-word passage). If we're building for current test-takers, question sets should be 5 per passage on ~200-word texts.

#### Source R2
- **URL:** https://www.toeflresources.com/blog/2026_toefl_format_revealed/ (TOEFL Resources — format announcement)
- **Core finding:** The new academic passage questions no longer indicate which paragraph to check. Test-takers must scan the full passage for each answer. In the old format, questions were presented with a paragraph reference (e.g., "In paragraph 2..."). This is a significant shift in how factual detail questions work — the answer location is no longer scaffolded.
- **Relevance:** Our question data model likely stores a `paragraph` or `location` field used to guide users. In the new format, this field is either absent or irrelevant — all questions reference the passage as a whole.

#### Source R3
- **URL:** https://testsucceed.com/materials/tests/toefl_new/en/description/toefl-2026-new-reading-description.html (TestSucceed, 2026 description)
- **Core finding:** Confirmed question types for the academic passage in 2026: vocabulary in context, factual details, negative facts, inferences, rhetorical purpose, sentence simplification. **Text insertion (sentence insertion) is explicitly NOT listed** for the new format.
- **Relevance:** Direct confirmation that `text_insertion` is a deprecated question type as of January 21, 2026.

---

### Q2 — TOEFL text_insertion (Sentence Insertion): Status in 2026 and Design Principles

#### Source R4
- **URL:** https://toefl.magoosh.com/toefl-2026-changes (Magoosh — comprehensive 2026 change guide)
- **Core finding:** Explicitly states: *"The new TOEFL 2026 doesn't have sentence insertion questions."* This is listed alongside the removal of 700-word passages and prose summaries as the three defining structural removals. The question type existed in the pre-2026 format where four black square markers [■] were placed at potential insertion points in a paragraph, and test-takers chose which position best fits a provided sentence.
- **Relevance to app:** Any `text_insertion` questions currently in our reading question bank are **testing a question type that no longer appears on the actual TOEFL**. This is a content accuracy problem, not just a feature gap.

#### Source R5
- **URL:** https://ieltsix.com/toefl/toefl-reading/insert-text-questions/ (IELTSix — pre-2026 insertion guide)
- **Core finding (pre-2026 design principles for reference):**
  - Always **4 answer choices** (positions A/B/C/D marked with ■ in the passage).
  - Exactly **1 correct answer per question** — a well-designed insertion question has only one logically sound location.
  - The inserted sentence must connect grammatically AND logically: the sentence before must introduce the topic or context, and the sentence after must follow from it.
  - Common insertion cue patterns: (a) pronoun reference — the inserted sentence contains "they/it/this" that refers to a noun just introduced in the preceding sentence; (b) contrast markers — the inserted sentence begins with "However/Nevertheless" which must follow a positive claim; (c) logical sequence — general→specific, cause→effect, background→development.
  - **Distractor design:** Wrong positions typically break pronoun reference chains (referent appears *after* the blank, not before) or split cause/effect pairs that must stay adjacent.
- **Relevance:** If our app retains `text_insertion` questions as a legacy/practice feature, these are the design standards. The 4-choice, single-correct format is non-negotiable. The key quality signal: if more than one position feels defensible, the question is flawed.

#### Source R6
- **URL:** https://blog.testglider.com/how-to-answer-toefl-reading-sentence-insertion-questions/ (TestGlider)
- **Core finding:** The most common design flaw in practice `text_insertion` questions (from test-prep materials, not ETS) is inserting a sentence that could fit 2 or more positions because the passage itself lacks clear cohesion signals (e.g., no pronouns, no discourse markers). ETS-quality insertion questions are identifiable because one position contains a pronoun "this/these/they" that requires the inserted sentence's noun as an antecedent — creating a clear grammatical dependency chain.
- **Relevance:** For our question quality audit: any `text_insertion` question where the passage doesn't have a clear pronoun-antecedent chain or discourse-marker contrast should be flagged as potentially ambiguous.

---

### Q3 — TOEFL Reading Question Type Distribution (Pre-2026 and 2026)

#### Source R7
- **URL:** https://magoosh.com/toefl/toefl-reading-question-type-overview/ (Magoosh — question type overview)
- **Core finding (pre-2026 old format — 10 questions per passage):**
  - **Factual Information:** 1–3 per passage (most frequent single type, ~15–25% of passage questions)
  - **Negative Factual (NOT/EXCEPT):** 0–2 per passage (~10–15%)
  - **Inference:** 1–2 per passage (~10–15%)
  - **Vocabulary (closest in meaning):** 2–3 per passage (~20–25%, second most frequent)
  - **Rhetorical Purpose:** 1–2 per passage (~10%)
  - **Sentence Simplification:** 0–1 per passage (rare, ~5–10%)
  - **Text Insertion:** 0–1 per passage (rare, ~5–10%)
  - **Reference:** 0–1 per passage (~5%)
  - **Prose Summary / Fill-in-Table:** 1 per passage, multi-select, 2–3 points (always final question)
  - **Note:** ETS does not publish exact percentage breakdowns. These ranges are derived from analysis of official practice tests.

- **2026 new format (5 questions per ~200-word academic passage):**
  - With only 5 questions, expect approximately: 1–2 vocabulary, 1–2 factual/negative factual, 1 inference or rhetorical purpose, 0–1 sentence simplification. Text insertion and prose summary are confirmed absent.
  - The compressed format means lower-frequency types (sentence simplification, reference) may appear rarely or not at all on any given passage.

#### Source R8
- **URL:** https://www.bestmytest.com/blog/toefl/toefl-reading-question-types (BestMyTest — 10 types breakdown)
- **Core finding:** In the pre-2026 format, vocabulary questions were the most frequently practiced question type in third-party prep materials because they appeared 2–3 per passage and were considered the most trainable. Negative factual questions (NOT/EXCEPT) were rated as the most time-consuming due to requiring elimination of 3 true statements. Sentence simplification appeared at most once per passage and was never repeated within a single passage.
- **Relevance:** For our question bank balance: if we're modeling the new 5-question format, having more than 1 vocabulary question or 1 negative factual question in a 5-question set is disproportionate to real test distribution.

---

### Q4 — Known Design Issues in Academic Passage Question Design

#### Source R9
- **URL:** https://blog.testglider.com/toefl-reading-questions-with-examples/ (TestGlider — question design analysis)
- **Core finding on factual_detail traps:**
  - The most common trap: answer choices that use **exact words from the passage but recontextualize them** — the vocabulary matches but the relationship between concepts is inverted (e.g., passage says A causes B; trap answer says B causes A).
  - Second most common trap: **scope mismatch** — a detail that is true in the passage but applies to a different subject than the question asks about (e.g., question asks about organism X, distractor states something true about organism Y mentioned in the same paragraph).
  - Third: **partial correctness** — the answer is true as far as it goes but omits a critical qualifier from the passage (e.g., passage says "under certain conditions X occurs"; distractor says "X occurs" without the qualifier).

#### Source R10
- **URL:** https://www.lingomelo.com/blog-page/toefl-reading-practice-guide/ (Lingomelo)
- **Core finding on pronoun reference questions:**
  - Reference questions (asking what "it," "they," "this," "which" refers to) are a distinct question type in the old format but are no longer a named type in the 2026 format — reference understanding is now tested implicitly through inference and rhetorical purpose questions.
  - Common ambiguity in poorly designed reference questions: the passage uses a pronoun that could grammatically refer to two nearby nouns of the same grammatical number and type. ETS-quality reference questions have only one grammatically possible antecedent within the sentence; proximity alone is used to distinguish in borderline cases.
  - In academic passage question design, pronoun ambiguity most frequently occurs when: (a) two plural nouns appear in the same sentence before a "they," (b) a relative clause creates a nested noun phrase making the closest-noun rule ambiguous, or (c) a demonstrative "this" follows a sentence with two candidate noun phrases.

#### Source R11
- **URL:** https://www.bestmytest.com/blog/toefl/toefl-reading-question-type-negative-factual-information (BestMyTest — negative factual analysis)
- **Core finding on negative_fact design issues:**
  - Negative factual questions are the highest-difficulty factual type because all three wrong answers must be explicitly and unambiguously stated in the passage, while the correct answer must be either directly contradicted OR simply not mentioned at all.
  - Design flaw in third-party practice materials: correct answers that are "not mentioned" are less valid than correct answers that are "directly contradicted" — "not mentioned" leaves room for the test-taker to argue it could be implied. ETS-quality negative factual questions prefer the directly-contradicted correct answer.
  - Second flaw: distractors that are only partially stated in the passage create ambiguity about whether they count as "mentioned." All three wrong-answer distractors must each be **fully and unambiguously** stated somewhere in the passage.

#### Source R12
- **URL:** https://study.com/resources/new-toefl-reading-tips.html (Study.com — 2026 reading guide)
- **Core finding:** In the new 2026 format, without paragraph references on questions, factual detail question design gains a new difficulty axis: test-takers must locate the relevant section unaided. This means well-designed factual questions for the 2026 format should have answer choices that are distinguishable without reading the entire passage — traps should be answerable by someone who reads carefully, not just someone who can locate the right paragraph quickly. The removal of paragraph scaffolding increases the cognitive load for all factual question types.

---

### Loop 3 Summary: Key Findings for App Development

| Finding | Impact | Action Required |
|---------|--------|-----------------|
| `text_insertion` removed from TOEFL as of Jan 21, 2026 | High — question type is now off-test | Flag `text_insertion` questions in bank as legacy; optionally disable or label "not on current TOEFL" |
| Academic passages are now ~200 words, 5 questions (not 700 words, 10 questions) | High — content structure mismatch | Audit passage length and question count targets in Reading question bank |
| Paragraph references removed in 2026 format | Medium — UI/data model | If question data stores paragraph location hints, they should not be surfaced to users practicing 2026 format |
| `sentence_simplification` still included in 2026 | Low — no change needed | No action |
| Prose summary / fill-in-table removed in 2026 | Medium | Audit for these in question bank; label as legacy if present |
| `negative_fact` correct answer should be "directly contradicted," not merely "not mentioned" | Medium — question quality | Audit existing `negative_fact` questions: correct answer should point to a contradiction in the passage, not an absence |
| Factual detail traps: inverted causation and scope mismatch are the canonical distractor patterns | Medium — question quality | Use as checklist when reviewing/generating factual questions |
| Pronoun reference ambiguity: two same-type nouns before "they/it" is the primary failure mode | Medium — question quality | Any reference or inference question using pronouns should verify single grammatically possible antecedent |

### Loop 3 Key Negative Findings

- **No official ETS percentage distribution exists** for question types per passage. All frequency data is derived from analysis of official practice tests by third-party sources.
- **Sentence simplification design is unchanged** — still max 1 per passage, still requires the paraphrase to preserve essential meaning while omitting minor details. No 2026 redesign.
- **text_insertion was not merely de-emphasized — it was fully removed**. No partial version or simplified variant appears in the 2026 format. Any question bank that includes it is testing a discontinued skill for current test-takers.

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
