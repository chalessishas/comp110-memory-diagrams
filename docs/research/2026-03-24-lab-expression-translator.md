# Research: Expression-Level AI Writing Assistance vs Full Text Generation

Date: 2026-03-24
Context: Designing Lab feature for Writing Center product. Core tension: AI assistance without ghostwriting.

## Key Finding 1: The AI Ghostwriter Effect (ACM TOCHI)

- Source: https://dl.acm.org/doi/10.1145/3637875
- Core: Users don't feel ownership of AI-generated text but still claim authorship publicly
- **Critical for us**: "Subjective control over the interaction and the content increases the sense of ownership" — design choices directly impact whether students feel they wrote it
- Implication: If Lab generates full articles, users won't feel ownership even if ideas are theirs. Sentence-level choices preserve ownership feeling.

## Key Finding 2: Sentence-Level Tools Preserve Authorship

- InstaText (https://instatext.io/academic-writing/) — "refines writing while preserving authorship, unique voice, style, and intent. Users accept or reject each suggestion—nothing changes without approval"
- Jenni AI — autocomplete suggests next part of sentence based on what you've written + uploaded research. "Less like an AI writer, more like an assistant"
- QuillBot — sentence-level rewriting, not full generation. "Improves expression, not core thinking"
- **Pattern**: Successful educational tools operate at expression level (word/sentence), not content level (paragraph/essay)

## Key Finding 3: Academic Integrity Best Practice

- Source: https://www.frontiersin.org/journals/communication/articles/10.3389/fcomm.2025.1598988/full
- "Benefits typically occur when students remain the primary authors and use AI output as suggestions rather than replacements"
- "When students rely on AI for authorship, their writing tends to be more generic, less aligned with disciplinary conventions"
- The 'tapas model' of assessment: pure human work, bounded AI use, and full AI integration — we should design for "bounded AI use"

## Key Finding 4: Three Roles for GenAI in Education

Students engaged with GenAI in three primary roles:
1. **Course guide** — explaining concepts
2. **Writing coach** — feedback and suggestions (= our Writing Center)
3. **Research partner** — helping find and synthesize sources

None of these roles is "ghostwriter." Our Lab should fit into role 2 or 3, not be a new role 4.

## Competitive Landscape

| Tool | Level | Generates Full Text? | Student Ownership |
|------|-------|---------------------|-------------------|
| QuillBot | Sentence rewrite | No | High — user controls each change |
| InstaText | Sentence refine | No | High — accept/reject per suggestion |
| Jenni AI | Sentence autocomplete | Partial | Medium — suggests continuations |
| Paperpal | Academic translation | No | High — translation options |
| ChatGPT | Full text | Yes | Low — ghostwriter effect |
| **Our Lab (original)** | **Full text from dialogue** | **Yes** | **Low** |
| **Our Lab (proposed B)** | **Sentence expression options** | **No** | **High** |

## Recommendation for Lab Design

The research strongly supports the sub-agent's recommendation B (Expression Translator):

1. **Operate at sentence level, not document level** — this is the line between "writing coach" and "ghostwriter"
2. **Offer options, not outputs** — show 2-3 expression alternatives, let user choose/modify
3. **Preserve user control** — nothing enters the document without explicit user action
4. **Use conversation for ideation, not generation** — dialogue helps user think, not produce text

This aligns with the user's stated philosophy: "AI helps efficiently convey ideas, not replace thinking; long-term vision is personalized translator."
