# CourseHub — Next Evidence-Based Features Research
Generated: 2026-04-10 10:01:08

## Already Shipped (baseline)
Retrieval practice, FSRS spaced repetition, adaptive difficulty (85% rule), metacognitive confidence calibration, teach-back (self-explanation g=0.48), explanation gating, misconception tracking, interleaving, session summary modal.

---

## Research Findings

### 1. Deliberate Error Analysis (2025)
**Source:** "Learning from errors: deliberate errors enhance learning" (ScienceDirect 2025); "Deliberate Erring Improves Far Transfer" PMC

Deliberately writing wrong answers and then correcting them outperforms errorless generation for **far transfer** (applying concepts to novel problems). The mechanism: forcing articulation of why the wrong answer was tempting triggers deeper encoding than passive review of the correct answer.

*Effect on CourseHub:* Our explanation gating (click to reveal after wrong) is passive. Adding an active "why did you choose this?" reflection step before reveal upgrades it to deliberate error analysis.

**Actionable proposal:** After a wrong MC answer, show a 1-line prompt: "In one sentence, why did [wrong option] seem correct?" → user types briefly → then reveal full explanation. AI not required — the act of typing is sufficient. Store reflection text for later review.

**Implementation cost:** Low — modify `QuestionCard.tsx` wrong-answer state machine. No new API needed.
**Expected impact:** High (far transfer, not just retention of memorized answers)

---

### 2. Elaborative Interrogation Prompts (2025)
**Source:** "Effective Use of Elaborative Interrogation to Improve Academic Performance" (Reading Psychology, 2025); meta-analysis d=0.55–0.61 for self-explanation

Elaborative interrogation ("Why is this true?") shows d=0.55 vs. control for near transfer. Most effective for learners who have some prior knowledge (not complete novices). Self-explanation prompts on posttest items improved immediate learning (d=0.61) but not long-term retention alone — needs combination with retrieval practice.

*Effect on CourseHub:* The teach-back panel is a full self-explanation but it's optional and only available after lesson chunks. A lighter-weight "why?" prompt could be inserted into the FSRS review queue.

**Actionable proposal:** In the review page, add an optional "Explain it" quick-response field below the question — before flipping the card. Pre-populated placeholder: "Explain why the answer is [answer] in your own words." User types, submits, then sees full explanation. No AI needed for grading.

**Implementation cost:** Medium — adds a new state to `QuestionCard` for FSRS review mode specifically.
**Expected impact:** Medium (d=0.55 but requires user engagement; optional keeps friction low)

---

### 3. Upcoming Review Schedule Visibility
**Source:** Spaced practice compliance literature — distributed practice d=0.54 PMC 2025; physician spaced repetition study PubMed 2024

FSRS calculates exact due dates per card but CourseHub only shows current due count. Research on physician SRS use shows **schedule visibility significantly improves compliance** — knowing "5 cards due Thursday" motivates users to plan study sessions.

*Effect on CourseHub:* Users see a "N cards due" badge on the course card but no forward-looking schedule. This makes it hard to plan ahead.

**Actionable proposal:** Add a small "Next 7 days" sparkline to the review page header — showing bar heights for Mon–Sun based on FSRS due dates from localStorage `loadCards()`. No backend needed, pure client-side from existing card state.

**Implementation cost:** Low — read from existing `loadCards()`, group by `dueDate`, render 7 bars.
**Expected impact:** Medium (compliance/adherence improvement, not direct learning effect)

---

## Prioritized Recommendations

| Priority | Feature | Research basis | Implementation cost | Expected impact |
|----------|---------|----------------|---------------------|-----------------|
| 1 | **Wrong-answer reflection prompt** | Deliberate error d>0.54, far transfer | Low (QuestionCard state) | High |
| 2 | **7-day review schedule sparkline** | Distributed practice compliance d=0.54 | Low (client-side only) | Medium |
| 3 | **Elaborative "why?" prompt in review** | Self-explanation d=0.55–0.61 | Medium (new QuestionCard state) | Medium |

**Skip for now:** Quick Retry in session summary (research supports massed practice being worse than spaced; immediate retry is counter-FSRS). Metacognitive calibration UI already fully shipped.

---

## Sources
- [Distributed Practice Meta-Analysis PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12189222/)
- [Spaced Learning in Radiology Education ScienceDirect](https://www.sciencedirect.com/science/article/pii/S1546144023006464)
- [Retrieval Practice in Health Professions PMC 2025](https://pmc.ncbi.nlm.nih.gov/articles/PMC12292765/)
- [FSRS in Practicing Physicians PubMed 2024](https://pubmed.ncbi.nlm.nih.gov/39250798/)
- [Deliberate Errors Improve Far Transfer PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC9902256/)
- [Learning from Errors 2025 Review PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC11803059/)
- [Elaborative Interrogation 2025 Reading Psychology](https://www.tandfonline.com/doi/full/10.1080/02702711.2025.2482627)
- [Self-Explanation Meta-Analysis Northeastern](https://learning.northeastern.edu/the-power-of-self-explanation/)
