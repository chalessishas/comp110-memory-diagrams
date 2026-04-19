# Research Loop — 2026-04-18 20:06 New Project Discovery

**Trigger**: Automated Research Loop (hourly)
**Agent**: sonnet-0418d
**Previous loop**: sonnet-0418b @ 20:01 (4 min ago — tight gap, new trigger)

---

## What Changed Since Last Research Loop

### TOEFL m6 negative_fact — DONE ✅
Progress Loop sonnet-0418c (20:04) executed the top recommendation from last research loop:
- Commit `1c43e8f` — added `negative_fact` question to m6 CPH passage
- All 6 academic passages now have complete 9-question-type coverage
- Pushed to TOEFL main

### New Untracked Project: `docs/comp110-redesign/`

This directory was **not present in the last research loop**. It contains:

| File | Description |
|------|-------------|
| `DESIGN_BRIEF.md` | Full 200-line design spec for COMP110 website redesign |
| `mockup.html` | Static HTML prototype (browser-renderable) |

Also in workspace root (likely related artifacts):
- `comp110_mockup_full.png` — full-page screenshot
- `comp110_mockup_viewport.png` — viewport screenshot
- `mockup.html` (root level — possibly older version)
- `DESIGN_BRIEF.md` (root level — possibly older version, also untracked)

**Project summary**: Redesign Kris Jordan's COMP110 course website (UNC CS) from Bootstrap/2024-era aesthetic to a modern 2026 education UI. Key features:
- Carolina yellow (#F5B700) brand color preserved
- Inter/SF Pro typography
- Card-based agenda with filter chips + 3 view modes
- Right-side sidebar (Next Up / Quick Links / Topic Index)
- Right-bottom AI TA FAB (collapsible, context-aware, DeepSeek-backed)
- prefers-color-scheme dark mode

**Phase status** (per DESIGN_BRIEF.md):
- Phase 1 (Design/Mockup): ✅ Complete
- Phase 2 (Next.js implementation): ⏳ Ready to start — user hasn't asked yet
- Phase 3 (agenda.json data): ⏳ Needs scripting
- Phase 4 (AI TA + RAG): ⏳ Future
- Phase 5 (Kris Jordan authorization): User action required

**This project is NOT in CLAUDE.md's project table** — it's a new initiative.

---

## Remaining Items from Last Research Loop

| Item | Status |
|------|--------|
| TOEFL m6 negative_fact | ✅ Done (1c43e8f) |
| Signal-Map Prisma 7 config migration | ⏳ Still pending — no blocker |
| TOEFL "Fill in a Table" question type | ⏳ Still pending — no blocker |
| ai-text-detector Ollama provider | ⏳ Needs Ollama env check |

---

## Recommendations

1. **[High]** When user returns, ask if they want to proceed with Phase 2 of comp110-redesign (Next.js + Tailwind). The brief explicitly mentions using DeepSeek-Coder or Claude Code — we can start immediately once user confirms.
2. **[Medium]** Add comp110-redesign to CLAUDE.md project table so future loops track it properly.
3. **[Low]** Signal-Map Prisma 7 migration is still a clean autonomous win (~10 lines) — safe to execute next Progress Loop if no higher priority work appears.
