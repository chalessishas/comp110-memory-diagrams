# Research Loop — 2026-04-18 23:02 — Arknights Sim Data Pipeline Audit

## Context

Previous session (opus-0418AE/AD) identified data quality issues in manually-curated `data/characters/` files and left two decisions open:
- **Path A**: manual PRTS hand-correction for core operators
- **Path B**: ArknightsGameData (akgd) auto-pipeline

This report resolves that open question and proposes a concrete execution path.

---

## Key Finding: gen_characters.py Is Already Working

`tools/gen_characters.py` was written, cached `character_table.json` locally, and already generated 6 operator files into `data/characters/generated/`. The tool **runs successfully right now** from cache (no network needed).

### Generated stats (E2 max-level, trust 0):
| Operator | HP | ATK | DEF |
|---|---|---|---|
| SilverAsh | 2560 | 713 | 397 |
| Liskarm | 3240 | 425 | 710 |
| Exusiai | 1673 | 540 | 161 |
| Hoshiguma | 3850 | 430 | 723 |
| Warfarin | 1520 | 505 | 125 |
| Angelina | 1385 | 542 | 120 |

### Divergence vs manually-curated files:
| Operator | HP delta | ATK delta | DEF delta | Severity |
|---|---|---|---|---|
| SilverAsh | -111 (-4.2%) | -10 (-1.4%) | +37 (+10%) | Low |
| **Liskarm** | **+1040 (+47%)** | **-70 (-14%)** | **+279 (+65%)** | **Critical** |
| **Exusiai** | **-675 (-29%)** | **-165 (-23%)** | +37 (+30%) | **Critical** |
| Hoshiguma | 0 | 0 | 0 | ✅ |
| Warfarin | 0 | 0 | 0 | ✅ |
| Angelina | 0 | 0 | 0 | ✅ |

Liskarm and Exusiai have severely wrong manual stats — these operators would behave wrong in any fight test.

---

## Git State: Uncommitted Chaos

Current `git status --short`:
```
 M core/systems/targeting_system.py    ← unstaged modifications
 M data/characters/__init__.py         ← unstaged modifications
?? data/characters/angelina.py         ← untracked (skill-capable manual file)
?? data/characters/generated/          ← untracked (6 akgd-generated files)
?? data/characters/hoshiguma.py        ← untracked
?? data/characters/warfarin.py         ← untracked
?? tools/                              ← untracked (gen_characters.py + cache)
```

The `data/characters/__init__.py` only exports 4 operators (`make_silverash`, `make_liskarm`, `make_exusiai`, `make_warfarin`). The newly-created `angelina.py`, `hoshiguma.py`, `warfarin.py` skill-aware files are not imported. `generated/` is entirely untracked.

---

## v2 ECS Coverage Gaps

Current v2 test coverage (14 tests):
- ✅ Enemy movement along path
- ✅ Operator blocking
- ✅ Combat damage (physical formula)
- ✅ DP accumulation + deploy gate
- ✅ Basic smoke tests

Missing in v2 (all in v1):
- ❌ Skill system integration (skill_system.py exists + register_skill() works, but zero v2 tests exercise skills)
- ❌ Enemy traits (aerial, invisible, arts_immune) — not ported from v1
- ❌ Stage loading via YAML
- ❌ Status effects (stun/slow) — implemented in v1 only
- ❌ Terrain effects — implemented in v1 only

---

## Recommended Execution Plan (Priority Order)

### P1 — Commit untracked files (5 min, no-risk)
Commit `tools/`, `data/characters/angelina.py`, `hoshiguma.py`, `warfarin.py`, `generated/`, and the two modified files. This is pure housekeeping.

### P2 — Fix Liskarm and Exusiai stats (15 min, high-value)
The generated files already exist. Two options:
- **Option 2a**: Replace stats in the manually-curated `data/characters/liskarm.py` and `exusiai.py` with akgd values, keeping the skill behavior intact (recommended — skills are not in generated files).
- **Option 2b**: Split: use generated file for stats, overlay skill components separately.

Recommend **2a**: surgically update the stat fields in the existing skill-aware files to match akgd values.

### P3 — Add v2 skill integration test (30 min)
SilverAsh's `skill_system.py` registration via `register_skill()` already works (used in `data/characters/silverash.py`). Add 1 test:
- Deploy SilverAsh with S3, let auto-SP accumulate, verify buff fires.

### P4 — Register angelina/hoshiguma/warfarin in __init__.py (5 min)
`data/characters/__init__.py` only exports 4 operators. Add the 3 new ones.

---

## Decision Resolution

**Path A vs Path B**: The answer is already **Path A executed** — `gen_characters.py` is Path B tooling, but since it ran to completion and outputs Python files, what we actually have is canonical stats in `generated/`. The remaining work is just **merging those stats into the skill-aware files** (Path A ergonomics, Path B data quality). No new tooling needed.

The `data/ingest/` directory is empty — the akgd fetcher stub referenced in `data/characters/__init__.py` was never written. This doesn't matter since `tools/gen_characters.py` covers that function.

---

## Sources

- ArknightsGameData character_table.json (cached at `tools/.char_table_cache.json`) — E2 max-level stats
- Live test runs: `pytest v1/tests` = 72 ✅, `pytest tests/` = 14 ✅
- git status (2026-04-18 23:02)
