# Prompt A/B Testing & AI Educational Content Evaluation — Research Summary

Date: 2026-04-09

## Purpose

Actionable research for CourseHub's prompt optimization pipeline: how to systematically test and improve Qwen 3.5-Plus prompts that generate questions, lessons, and explanations.

---

## 1. Prompt A/B Testing in EdTech — Industry Practice

### 1.1 Duolingo: Birdbrain + Prompt-Driven Content Generation

- **URL**: https://blog.duolingo.com/large-language-model-duolingo-lessons/
- **Core finding**: Duolingo structures prompts with fixed rules (exercise type constraints) and variable rules (course, difficulty level, lesson focus). AI generates multiple exercise variants; Birdbrain (their ML model) automatically evaluates each variant on difficulty scores and quality metrics, rejecting content that doesn't meet thresholds before human review.
- **Relevance to CourseHub**: Directly applicable pattern. CourseHub's `generate-questions` API could adopt a similar generate-then-filter pipeline: produce N question candidates per prompt, score each with automated metrics (difficulty alignment, distractor quality, Bloom's level), keep the best. Currently CourseHub generates and serves questions in a single pass with no quality gate.
- **Limitations**: Duolingo's Birdbrain is a custom ML model trained on millions of learner interactions — CourseHub doesn't have that data volume yet. The A/B testing infrastructure assumes large user bases for statistical power.

### 1.2 Duolingo: A/B Testing Philosophy

- **URL**: https://blog.duolingo.com/learning-how-to-help-you-learn-introducing-birdbrain/
- **Core finding**: Duolingo A/B tests every new ML model against large user populations. They treat testing as non-negotiable: "the only way to understand the impact of a new model on language learning is to A/B test against a large number of users."
- **Relevance to CourseHub**: Establishes the principle that prompt changes must be validated empirically, not just eyeballed. Even with CourseHub's smaller user base, structured offline evaluation (test sets + automated scoring) is the minimum viable version of this practice.
- **Limitations**: Duolingo has millions of DAU; CourseHub likely has hundreds. True online A/B testing requires alternative approaches (see Section 3).

### 1.3 Khan Academy Khanmigo: Efficacy Data

- **URL**: https://blog.khanacademy.org/khan-academy-efficacy-results-november-2024/
- **Core finding**: A WestEd longitudinal study found students using Khanmigo 30+ min/week showed 0.23 SD improvement in math (50th to 59th percentile). English Language Learners showed even larger gains (0.31 SD). However, engagement dropped 60% after 3 weeks without active teacher facilitation (Stanford CEPA finding).
- **Relevance to CourseHub**: Key metric benchmark — 0.23 SD is the bar for "meaningful AI tutoring impact." The engagement drop finding is critical: CourseHub needs retention mechanisms beyond pure AI content quality. The StudyTask and streak systems partially address this.
- **Limitations**: Khanmigo is GPT-4 based with extensive prompt engineering by a large team. Results may not transfer directly to Qwen 3.5-Plus. The study measured tutoring interactions, not standalone question/lesson generation quality.

### 1.4 Coursera & Broader EdTech AI Adoption

- **URL**: https://www.nature.com/articles/s41598-025-10941-y
- **Core finding**: A 37% increase in interdisciplinary project outcomes was observed when AI-generated content tools were strategically implemented. Metrics used: collaborative problem-solving scores, cross-domain knowledge integration ratings, peer evaluation. However, nearly half of students expressed reservations about AI content accuracy.
- **Relevance to CourseHub**: Validates that AI content can drive measurable learning gains when properly integrated. The accuracy concern reinforces the need for CourseHub's planned quality assurance pipeline (flagged questions, misconception injection).
- **Limitations**: Study focused on AIGC tools broadly (ChatGPT etc.), not on optimized prompt pipelines specifically.

---

## 2. Evaluation Frameworks for AI-Generated Teaching Content

### 2.1 Bloom's Taxonomy Alignment — Automated Classification

- **URL**: https://arxiv.org/html/2408.04394v1
- **Core finding**: Instruction fine-tuned LLMs can generate questions at specified Bloom's levels with 78% rated "High Quality" and 65.6% matching the intended cognitive level by human raters. Key challenge: GPT-4 struggles with higher-order levels (Analyzing, Evaluating). Best automated classifier: SVM with data augmentation achieved 94% accuracy on Bloom's classification.
- **Relevance to CourseHub**: **Directly actionable.** CourseHub's question generation prompts should specify the target Bloom's level explicitly. A post-generation classifier (even a simple LLM-as-judge call) can verify alignment. The 65.6% intended-level match rate is the baseline to beat.
- **Limitations**: 78% "high quality" still means 22% are not. Human expert review remains necessary for high-stakes content. The SVM classifier needs labeled training data that CourseHub doesn't have yet.

**Supporting source**:
- **URL**: https://journals.sagepub.com/doi/10.1177/1932202X251349917
- AI-generated questions align well with lower-order cognitive tasks (Remember, Understand) but show potential at higher levels in science and language arts. Human-generated questions still provide greater alignment overall.

### 2.2 Webb's Depth of Knowledge (DOK) Classification

- **URL**: https://teachquill.com/dok-question-generator
- **Core finding**: AI-powered DOK question generators now produce questions at specific cognitive rigor levels (Recall, Skill/Concept, Strategic Thinking, Extended Thinking). Key distinction: DOK measures complexity of thinking required, not difficulty. Questions can be exported organized by DOK level with standards tags.
- **Relevance to CourseHub**: DOK provides a complementary dimension to Bloom's. For exam prep (CourseHub's primary use case), DOK Level 3-4 questions are most valuable because they test strategic thinking, not just recall. CourseHub prompts should specify both Bloom's level AND DOK level for optimal question targeting.
- **Limitations**: No peer-reviewed research on automated DOK classification accuracy was found. The tools referenced are commercial products, not validated research instruments.

### 2.3 Item Response Theory (IRT) for Question Quality

- **URL**: https://arxiv.org/html/2508.08314v1
- **Core finding**: In a large-scale field study (91 classes, ~1700 students, dozens of colleges), AI-generated questions performed comparably to expert-created questions on IRT parameters. AI questions were somewhat easier but more discriminating than expert questions. The study used an iterative refinement strategy: generate -> critique -> revise cycles using LLM self-evaluation.
- **Relevance to CourseHub**: **High-impact finding.** The iterative refinement pattern (generate, LLM-critique, revise) is implementable today in CourseHub's pipeline without needing real student data. IRT parameters (difficulty, discrimination) can be estimated post-hoc from student attempt data that CourseHub already collects in the `attempts` table.
- **Limitations**: IRT calibration requires substantial response data per item (typically 200+ responses). CourseHub's per-question response volume is likely much lower. The study used GPT-4; Qwen 3.5-Plus performance on iterative refinement needs separate validation.

**Supporting source — AutoIRT**:
- **URL**: https://arxiv.org/html/2409.08823v1
- AutoIRT uses AutoML to calibrate IRT models from test response data + item content features. First use of AutoML for IRT fitting. Compatible with standard psychometric scoring and test administration.
- **Relevance**: Could eventually automate difficulty/discrimination estimation for CourseHub questions as response data accumulates.

### 2.4 Comprehensive Quality Metrics Beyond Accuracy

Based on multiple sources, the evaluation dimensions for AI-generated educational content:

| Dimension | What it measures | How to measure | Priority for CourseHub |
|-----------|-----------------|----------------|----------------------|
| **Bloom's level alignment** | Cognitive level matches intent | LLM classifier or SVM | P0 — directly affects learning value |
| **DOK level alignment** | Thinking complexity matches intent | Prompt-specified + LLM judge | P1 — important for exam prep |
| **IRT difficulty** | Item difficulty parameter | Computed from attempt data | P1 — needs data accumulation |
| **IRT discrimination** | Distinguishes high/low ability | Computed from attempt data | P1 — needs data accumulation |
| **Distractor quality** | MCQ wrong answers are plausible | LLM judge + attempt distribution | P0 — bad distractors = useless questions |
| **Content accuracy** | Factual correctness | LLM cross-check + user feedback | P0 — already partially tracked |
| **Pedagogical scaffolding** | Builds on prior knowledge | Knowledge graph alignment check | P2 — needs outline/KP structure |
| **Engagement** | Maintains learner interest | Time-on-task, completion rate | P2 — tracked via existing analytics |
| **Cognitive load** | Not too many concepts at once | Question length + concept count | P3 — lower priority |

---

## 3. Practical A/B Testing for LLM Prompts

### 3.1 The Braintrust Framework

- **URL**: https://www.braintrust.dev/articles/ab-testing-llm-prompts
- **Core finding**: Braintrust's approach: (1) Create multiple prompt variants as "tasks", (2) Run each against a shared evaluation dataset, (3) Score with automated evaluators (factuality, helpfulness, custom scorers), (4) Compare metrics side-by-side with confidence intervals. Key insight: LLM outputs are high-variance, so you need larger sample sizes than traditional A/B tests. Use power analysis before starting.
- **Relevance to CourseHub**: **Most directly applicable framework.** CourseHub can implement a lightweight version: maintain a golden test set of knowledge points, run each prompt variant against this set, score with LLM judges on accuracy/Bloom's alignment/distractor quality, compare results. No need for the full Braintrust platform — the methodology is what matters.
- **Limitations**: Braintrust is designed for production traffic splitting, which requires significant user volume. The offline evaluation approach (golden test set + automated scoring) is the practical path for CourseHub.

### 3.2 Statsig: Data-Driven LLM Optimization

- **URL**: https://www.statsig.com/blog/llm-optimization-online-experimentation
- **Core finding**: Statsig proposes three optimization axes for LLM A/B testing: (1) Prompt engineering — even small wording changes produce dramatically different outputs, (2) Model selection — larger models offer better accuracy at higher cost, (3) Parameter tuning — temperature/top-p control creativity vs consistency. For each, define a clear hypothesis, run controlled experiments, and use statistical analysis. Key metrics: conversation length, retention, click-through rates, and domain-specific quality scores.
- **Relevance to CourseHub**: The three-axis framework is useful for structuring CourseHub's optimization roadmap. Prompt wording is the immediate lever. Model selection (if Qwen releases new versions) is medium-term. Temperature tuning matters for question generation (lower temp for factual questions, higher for creative/analytical questions).
- **Limitations**: Statsig assumes production traffic volume for online experiments. For CourseHub, offline evaluation remains the practical starting point.

### 3.3 Langfuse: Open-Source Prompt Versioning + A/B Testing

- **URL**: https://langfuse.com/docs/prompt-management/features/a-b-testing
- **Core finding**: Langfuse provides open-source prompt versioning, trace-level tracking of which prompt version generated which output, and the ability to compare performance metrics between versions. Supports user feedback collection through ratings and automated evaluations at configurable sampling rates.
- **Relevance to CourseHub**: Langfuse is self-hostable and free — could be integrated into CourseHub's pipeline for prompt version tracking without vendor lock-in. The trace-level association (prompt version -> generated output -> student performance) is exactly the feedback loop CourseHub's quality assurance design calls for.
- **Limitations**: Requires integration effort. The evaluation capabilities are basic compared to Braintrust's AutoEvals.

### 3.4 Statistical Methods & Sample Size

Synthesized from Braintrust, Statsig, and the DEV Community guide (https://dev.to/kuldeep_paul/ab-testing-prompts-a-complete-guide-to-optimizing-llm-performance-1442):

**For CourseHub's context (small user base, educational content):**

| Method | When to use | Minimum sample | Notes |
|--------|------------|----------------|-------|
| **Offline eval with golden test set** | Every prompt change | 50-100 test cases per subject | Run prompt variants against fixed KPs, score with LLM judges. No real users needed. |
| **Paired comparison** | Comparing 2 prompt variants | 30+ generated pairs per variant | Same input, two outputs, LLM judge picks winner. Binomial test for significance. |
| **t-test on continuous metrics** | Comparing average scores | n ≥ 30 per group (ideally 100+) | For metrics like accuracy score, Bloom's alignment score. Check normality first. |
| **Chi-square test** | Comparing pass/fail rates | n ≥ 50 per group | For binary outcomes: "question meets quality threshold" yes/no. |
| **Bootstrap confidence intervals** | When distributions are weird | n ≥ 50 per group | Resample to estimate uncertainty. Good for small samples. |

**Critical pitfalls:**
1. Do NOT stop tests early when results "look good" — this inflates false positive rate
2. Use Bonferroni correction when testing multiple metrics simultaneously
3. LLM outputs are stochastic — same prompt + same input can produce different outputs. Run each test case 3-5 times and average
4. Minimum Detectable Effect (MDE): detecting a 10% improvement needs ~150 samples per group; detecting 5% needs ~600 per group

---

## 4. Recommended Action Plan for CourseHub

### Phase 1: Offline Evaluation Pipeline (1-2 weeks)

1. **Build a golden test set**: 20 knowledge points per subject area, with expected Bloom's levels and difficulty targets
2. **Implement LLM-as-judge scoring**: A separate Qwen call that rates each generated question on accuracy (0-5), Bloom's alignment (1-6 level), distractor quality (0-5), and clarity (0-5)
3. **Version prompt templates**: Store prompt variants with version IDs so every generated question traces back to which prompt produced it
4. **Run baseline measurement**: Score current prompts against the golden test set

### Phase 2: Iterative Refinement Loop (2-3 weeks)

1. **Implement generate-critique-revise cycle**: Based on the IRT field study pattern — generate a question, have a separate LLM call critique it, revise based on critique, then serve the improved version
2. **Add Bloom's/DOK level specification to prompts**: Explicitly request target cognitive levels in question generation prompts
3. **Wire feedback loop**: Connect existing `question_feedback` data and `attempts` data to prompt selection (as designed in the quality assurance doc)

### Phase 3: Online Measurement (ongoing)

1. **Track per-prompt-version metrics**: accuracy rate, avg attempts, time-to-answer, feedback sentiment
2. **Compute IRT parameters** once sufficient attempt data accumulates (~200 responses per question)
3. **Gradually introduce traffic splitting** between prompt variants as user base grows

---

## Sources Index

| # | Source | URL |
|---|--------|-----|
| 1 | Duolingo: LLMs for lesson creation | https://blog.duolingo.com/large-language-model-duolingo-lessons/ |
| 2 | Duolingo: Birdbrain introduction | https://blog.duolingo.com/learning-how-to-help-you-learn-introducing-birdbrain/ |
| 3 | Khan Academy: Efficacy results Nov 2024 | https://blog.khanacademy.org/khan-academy-efficacy-results-november-2024/ |
| 4 | Nature: AI content in higher education | https://www.nature.com/articles/s41598-025-10941-y |
| 5 | arXiv: Automated question generation at Bloom's levels | https://arxiv.org/html/2408.04394v1 |
| 6 | SAGE: AI questions for gifted education | https://journals.sagepub.com/doi/10.1177/1932202X251349917 |
| 7 | TeachQuill: DOK question generator | https://teachquill.com/dok-question-generator |
| 8 | arXiv: AI-generated exam quality field study (Stanford/Harvard) | https://arxiv.org/html/2508.08314v1 |
| 9 | arXiv: AutoIRT calibration | https://arxiv.org/html/2409.08823v1 |
| 10 | Braintrust: A/B testing LLM prompts guide | https://www.braintrust.dev/articles/ab-testing-llm-prompts |
| 11 | Statsig: Data-driven LLM optimization | https://www.statsig.com/blog/llm-optimization-online-experimentation |
| 12 | Langfuse: Prompt A/B testing docs | https://langfuse.com/docs/prompt-management/features/a-b-testing |
| 13 | DEV Community: A/B testing prompts guide | https://dev.to/kuldeep_paul/ab-testing-prompts-a-complete-guide-to-optimizing-llm-performance-1442 |
| 14 | arXiv: Bloom's Taxonomy classification (SVM, 94% accuracy) | https://arxiv.org/abs/2511.10903 |
| 15 | Braintrust: LLM evaluation metrics guide | https://www.braintrust.dev/articles/llm-evaluation-metrics-guide |
