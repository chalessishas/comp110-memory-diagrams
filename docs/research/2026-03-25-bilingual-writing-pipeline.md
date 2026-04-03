# Research: Bilingual Writing Pipeline — Chinese Ideation → English Expression

Date: 2026-03-25
Context: User's core vision is "个性化 translator" — AI helps ESL students express ideas they already have. Auto mode should support thinking in Chinese, writing in English.

## The Core Problem (from Research)

"EFL students who are tasked with producing written text in English often compose their ideas in their first language (L1) and then struggle mentally to translate those ideas into English."
— Source: https://www.degruyterbrill.com/document/doi/10.1515/dsll-2025-0001/html

This is exactly what our auto mode should solve. The user thinks in Chinese → provides ideas in Chinese → AI writes in English. Current auto mode already supports `language` parameter, but the flow assumes input and output are the same language.

## How Chinese Students Actually Use AI (BYU Study 2025)

Source: https://scholarsarchive.byu.edu/journalrw/vol11/iss2/1/

Key findings from studying Chinese ESL students at a Sino-American university:
1. Students primarily use GenAI in **early stages** (brainstorming, ideation) — exactly our checkpoint phase
2. Students use GenAI for **information retrieval** throughout the process
3. **Ethical concerns discourage** students from incorporating AI-generated text directly
4. Students engage in **code-switching** between Chinese and English during ideation

**Implication:** Our "you think, we write" model addresses #3 (ethical concern) by being transparent about AI writing. But we should explicitly support #4 (code-switching) — let users type in Chinese at checkpoints even when the output language is English.

## Paperpal: The Closest Competitor Model

Source: https://paperpal.com/blog/news-updates/how-paperpal-is-enhancing-academic-productivity-and-accelerating-research-in-china

Paperpal is used by 13,800+ Chinese academics and students. Their key insight:
- **"Chinese academics often wrote in Chinese first and then translated it into English"** — this is the natural workflow
- Paperpal's Translate feature: 50+ languages, academic-aware translation
- Users found "real-time language checks, precise academic translation, paraphrasing assistance" most valuable

**Difference from us:** Paperpal translates existing text. Our auto mode generates text from ideas. We're one level higher in the abstraction chain: Paperpal = Chinese text → English text. Us = Chinese ideas → English essay.

## Proposed Feature: Cross-Language Auto Mode

**Current flow:**
```
[Chinese checkpoint input] → language: "zh" → [Chinese essay output]
[English checkpoint input] → language: "en" → [English essay output]
```

**Proposed flow:**
```
[Chinese checkpoint input] → inputLang: "zh", outputLang: "en" → [English essay output]
```

User types thesis in Chinese: "社交媒体对学生注意力有害但促进协作学习"
AI writes the essay in English, faithful to the Chinese ideas.

### Implementation

1. Split `language` into `inputLanguage` and `outputLanguage` in PipelineState
2. Checkpoint UI uses `inputLanguage` for placeholder text
3. Draft prompt receives both: "The user's ideas are in Chinese. Write the essay in English. Faithfully express their ideas — do not add, remove, or reinterpret."
4. Analyze/grammar prompts use `outputLanguage`

**Effort:** ~20 lines changed (PipelineState + prompt templates + Workbench UI with two language toggles)

### Why This Matters for Positioning

| Tool | Input | Output | Level |
|------|-------|--------|-------|
| DeepL | Chinese text | English text | Translation |
| Paperpal | Chinese draft | English draft | Academic translation |
| Grammarly | English text | Better English text | Polish |
| ChatGPT | English prompt | English essay | Generation |
| **Our Auto Mode** | **Chinese ideas** | **English essay** | **Cross-language ideation → expression** |

No existing tool does Chinese ideas → English essay with a structured block pipeline. This is a genuine gap.

## KIMI's Approach (Relevant)

Source: https://journals.sagepub.com/doi/10.1177/20965311241310881

KIMI (a Chinese AI tool) has "bilingual processing and context-sensitive explanations" that "fostered students' emerging multilingual awareness, allowing them to compare language forms and reflect on cultural nuances in writing."

**Takeaway:** After auto mode generates the English essay, showing a side-by-side view of "your Chinese ideas" vs "English expression" could be educational AND help users verify the AI captured their intent.

## Concrete Next Steps

1. **Quick win (1 hour):** Add `inputLanguage` / `outputLanguage` split to AutoExecutor. Default both to same language. Add UI toggle "Think in 中文, write in English."
2. **Draft prompt update:** Add cross-language instruction when input ≠ output language
3. **Post-MVP:** Side-by-side view showing Chinese input → English paragraph mapping
4. **Post-MVP:** Integration with user's "Expression Translator" research (sentence-level options for how to express a Chinese idea in English)

Sources:
- [Chinese ESL Students & GenAI (BYU 2025)](https://scholarsarchive.byu.edu/journalrw/vol11/iss2/1/)
- [AI in L2 Writing Education (De Gruyter 2025)](https://www.degruyterbrill.com/document/doi/10.1515/dsll-2025-0001/html)
- [Paperpal in China](https://paperpal.com/blog/news-updates/how-paperpal-is-enhancing-academic-productivity-and-accelerating-research-in-china)
- [KIMI Bilingual Processing](https://journals.sagepub.com/doi/10.1177/20965311241310881)
- [AI-Powered L2 Writing Skills](https://www.mdpi.com/2076-3417/15/14/8079)
