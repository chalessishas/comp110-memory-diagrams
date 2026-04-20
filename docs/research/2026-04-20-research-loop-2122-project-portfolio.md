# Research Loop — Project Portfolio Review
**Timestamp:** 2026-04-20 02:26  
**Agent:** sonnet-0420 (Research sub-agent)  
**State:** arknights-sim at 1300 tests, P26/P51 just landed

---

## 1. arknights-sim — Missing Mechanics (Combat Accuracy)

### 1.1 Elysium Talent: "Standard Instruction" — VERIFIED CORRECT
`elysium.py` already implements the talent correctly:
- `+0.3 SP/s` to all deployed Vanguard operators (on_tick, aura pattern)
- `TalentComponent` registered, `register_talent` wired
- **No gap here.** The search result mentioning "Sniper Support" is incorrect for Elysium — that is actually a **different operator** (Elysium's talent in game is Standard Instruction: Vanguard SP buff). The Sniper ASPD buff mentioned in search is not Elysium's talent. Elysium is correctly implemented.

### 1.2 Hoshiguma — Silent Bug (HIGH PRIORITY)
`hoshiguma.py` creates `TalentComponent(behavior_tag="hoshiguma_overweight")` but **never calls `register_talent`**. The talent object exists on the unit but fires nothing. The `_OVERWEIGHT_TAG` is defined but only used in the `TalentComponent`, not in a `register_talent()` call.

**Fix required:** Add `on_hit_received` callback for the "Overweight" talent (reduce damage by 20% when HP > 50%). This is a silent correctness bug — tests pass because no test exercises the damage reduction path.

**Files:** `/Users/shaoq/Desktop/VScode Workspace/arknights-sim/data/characters/hoshiguma.py`

### 1.3 Operators With No Talent Implemented (16 operators)

Priority tier by combat impact:

**TIER 1 — High combat impact (implement soon):**
| Operator | Missing Talent | Mechanic Type |
|----------|---------------|---------------|
| Exusiai | Masterwork (each attack: chance to gain SP) | on_attack_hit |
| Ifrit | Inspiration: DEF reduction on hit | on_attack_hit |
| Silence | Healing critical chance (increases HoT on crit) | on_tick |
| Lumen | SP recovery bonus when healing | on_attack_hit |
| Saileach | All Vanguards gain SP at deployment | on_battle_start |

**TIER 2 — Meaningful but situational:**
| Operator | Missing Talent |
|----------|---------------|
| Vigil | Wolfpack damage boost per wolf on field |
| Leizi | Chain lightning arcs per SP held |
| Chen | Sword spawn on kill + summon lifecycle |

**TIER 3 — Minor/niche:**
- ashlock, courier, erato, headb2, rope, shaw, typhon (typhon has ammo, skill is done; talent is secondary)

### 1.4 Known Correctness Bugs From Prior Research (still open)

From `/arknights-sim/docs/research/*.md` (confirmed not yet fixed):

1. **Texas DP talent is wrong**: Current `texas_dp_on_kill` should be `texas_dp_on_battle_start` (flat 2 DP at squad entry, not per kill). File: `data/characters/texas.py`
2. **Charger trait missing class-level dispatch**: Fang, Vigna, Plume get DP on kill via class trait — this should be auto-attached in `spawn_system.py` for all `subclass == Charger` operators, not require per-operator talent tags.
3. **ATK buff pipeline FLOOR ordering**: Risk of accumulated rounding error if floors aren't applied in the correct order (base×stage, then ×percent multipliers).

### 1.5 Missing ECS Primitives (Architecture Gaps)

- **SP gain on hit (attack)**: Several talents grant SP per attack (Exusiai, Sesa). The `on_attack_hit` hook exists but no operator uses it for SP gain yet — it works, just unused for this pattern.
- **Global effect scope**: SilverAsh Silver Sword (P26) uses TTL re-stamp for global aura. Elysium uses a loop in `on_tick`. No unified "global aura" helper exists — each operator reimplements the pattern. Low debt now, will compound past ~10 aura operators.
- **Stacking status effects with independent durations**: Shamare (P17) uses 2-stack cap. No operator yet needs 3+ stacks with per-stack expiry. Will become complex if stacking Bind/Fragile operators are added.

---

## 2. comp110-redesign Phase 2 — Unblock Assessment

### Phase 2 Scope (from DESIGN_BRIEF.md)
- Next.js scaffold + 5-page skeleton + AI TA overlay UI
- Blocked on: "DeepSeek implementation"

### What "DeepSeek" actually means here
The brief uses DeepSeek for the AI TA backend (`chat/completions` API). The system prompt template is already written and embedded in the brief. The mockup HTML is done.

**DeepSeek API is publicly available** as of April 2026 at api.deepseek.com. No special access needed.

### Concrete unblock steps (3-4 hours of work)
1. `npx create-next-app comp110-26s` — 30 min
2. Port the mockup HTML to React components — 2 hours (5 components: Nav, AgendaCard, BadgeChip, Sidebar, AITAFloat)
3. Wire AI TA float to `api.deepseek.com/chat/completions` with the existing system prompt from the brief — 1 hour
4. Deploy to Vercel — 30 min

**Blocker:** DeepSeek API key. User needs to provide `DEEPSEEK_API_KEY` for the chat endpoint. Everything else is self-contained.

**Recommendation:** Unblock Phase 2. The design spec is complete, the system prompt exists, DeepSeek API is public. Only thing needed from user is the API key. This is a 4-hour implementation task.

---

## 3. Technical Debt in arknights-sim

### Debt Level: LOW-MODERATE (manageable, not urgent)

**Accumulating patterns:**
- **Per-operator aura re-implementation**: Elysium, SilverAsh, Mlynar, Pallas all do `on_tick` global buff loops independently. No shared utility. At ~10+ aura operators this will be fragile.
- **`_saved_*` attribute sprawl**: Skills that save/restore state (`_saved_block`, `_saved_atk`, `_saved_range`) use setattr with per-operator string keys. No schema enforcement — typos are silent bugs.
- **Test file naming inconsistency**: `test_v2_*` (most), `test_p9_*` (v1 legacy in `v1/tests/`). The v1 tests run in the same pytest session but test different ECS versions.
- **No integration test for squad composition**: All tests exercise single operators. No test validates that `SilverAsh + 3 melee allies` produces the correct combined ATK output in a realistic fight.

**Not yet a problem but watch:**
- `world.global_state.refund_dp()` called from skill ticks without bounds checking. If a skill fires after battle end, this could corrupt state.
- Event queue (`world.events`) has no size cap. Shouldn't matter at current simulation scale (<100 events per fight).

---

## 4. HOLD Projects — Priority Order

### Most likely to need attention soon: **Signal-Map**

**Reason:** It's live at hdmap.live. Real users. Any data source change (UNC changing API format, Supabase plan limits, Vercel cold starts) will break the live product without warning. No monitoring or alerting mentioned in STATUS.md.

**Specific risk:** The AI radio uses DashScope TTS — if DashScope changes pricing or API format, the radio breaks silently.

**Recommended action:** Add a simple uptime check (cron fetch to `/api/health`) + Discord notification when it fails. 1 hour of work, eliminates operational blindspot.

### Second priority: **TOEFL**

**Reason:** Fully implemented but undeployed due to missing Vercel secrets. The longer it sits undeployed, the more likely dependency drift will cause breakage. React Router 7 + Vite 6 have active release cycles.

**Unblock:** User provides Vercel env secrets. 30-minute deploy task once keys are available.

### Third: **ai-text-detector**

No STATUS.md found — unknown current state. Lower priority unless user has active need.

### Keep HOLD: **comp110-redesign**

Phase 1 is done. Phase 2 is a discrete 4-hour task. No time pressure (semester is ending soon, may want to target fall 2026 semester start).

---

## 5. Recommended Next P-steps for arknights-sim

In priority order:

| P# | Task | Effort | Impact |
|----|------|--------|--------|
| P27 | Fix Hoshiguma silent bug (register_talent + on_hit_received damage reduction) | 1 hr | High (correctness) |
| P28 | Fix Texas talent (dp_on_kill → dp_at_battle_start) | 30 min | High (correctness) |
| P29 | Exusiai talent (Masterwork: chance SP per attack hit) | 1 hr | High |
| P30 | Ifrit talent (DEF reduction on hit, FRAGILE-like) | 1 hr | High |
| P31 | Charger class trait auto-attach in spawn_system.py | 2 hr | Medium (architecture) |
| P32 | Silence talent (healing crit) | 1.5 hr | Medium |
| P33 | Saileach talent (Vanguard SP on deploy) | 1 hr | Medium |

---

*Sources consulted: arknights.wiki.gg (Elysium page), ak.gamepress.gg (talent list), arknights.fandom.com (Elysium overview). On-disk research doc confirmed existing bugs still open as of this scan.*
