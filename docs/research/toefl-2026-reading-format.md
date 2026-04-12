# TOEFL 2026 Reading Format Research

**Date:** 2026-04-12
**Relevance:** Platform currently has 6 academic passages with legacy question types (vocab, detail, inference, negative_fact, sentence_simplification, text_insertion, attitude, purpose, multiple). TOEFL 2026 format has fundamentally changed.

## Key Findings

- **Format overhaul effective January 21, 2026**: Reading section is now multistage adaptive, 18-27 minutes, 35-48 questions total across two modules. Second module difficulty adapts based on first module performance.
- **Passages are now ~200 words** (down from 700 words). Old 700-word academic passages no longer reflect the real test format.
- **Three question task types replace the legacy set**:
  1. `complete_the_words` — fill in missing letters in academic text (vocabulary + context)
  2. `read_in_daily_life` — short 15-150 word everyday texts (emails, memos, posters) testing main idea + key details
  3. `read_academic_passage` — ~200-word academic text with 5 MCQ per passage
- **Prose summary and fill-in-a-table are NOT in the new format.** These were legacy question types from the pre-2023 format. The new format does not include them, nor does it include sentence_simplification or text_insertion.
- **Scoring changes to 1-6 band scale** (alongside the existing 0-120 scale) starting January 2026.

## Source URLs

- https://www.toeflresources.com/blog/2026_toefl_format_revealed/
- https://www.ets.org/toefl/test-takers/ibt/about/content/reading.html
- https://www.bestmytest.com/blog/new-toefl-format-changes
- https://mliesl.edu/contents/the-new-toefl-ibt-2026-all-the-changes-you-need-to-know/

## Recommendation

**Most actionable change: retire legacy question types and add `read_in_daily_life` module.**

The platform's current academic passage format (pack6.js, 6 long passages) is obsolete for TOEFL 2026 test-takers. Priority order:

1. Add short `read_in_daily_life` passages (emails/memos/posters, 15-150 words) with MCQ — this is a new question category completely absent from the platform
2. Shorten existing academic passages from 700 to ~200 words, reduce to 5 questions per passage
3. Add `complete_the_words` fill-in-letters exercises (the existing `CompleteWords.jsx` may partially cover this)
4. Retire `sentence_simplification`, `text_insertion`, `negative_fact` question types — they no longer appear on the test
5. Implement adaptive difficulty: track per-session accuracy and increase difficulty in "module 2" if module 1 was >70% correct
