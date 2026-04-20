# Arknights Simulator v2 — Mechanics Gap Analysis
**Date:** 2026-04-19  
**Researcher:** sonnet-0419d  
**Target project:** `/Users/shaoq/Desktop/VScode Workspace/arknights-sim/`  
**Baseline:** 663 tests green, P1-P4 phases complete

---

## 1. Executive Summary

The simulator has strong coverage of core combat mechanics (damage formulas, status effects, SP recovery modes, AoE/chain/push/pull, aerial targeting). Major gaps fall into three categories: (a) entire archetype classes not yet implemented, (b) the Elemental Injury subsystem only scaffolded but not wired, and (c) timing/accuracy issues endemic to fan simulators that reduce simulation fidelity.

---

## 2. Archetype Coverage Gaps

### 2.1 Confirmed Missing Archetypes (from `core/types.py` RoleArchetype enum)

The enum defines these archetypes but no hand-authored character data files or system logic exists for them:

| Archetype | Key Mechanic | Representative Operators |
|-----------|-------------|--------------------------|
| `GUARD_MUSHA` | Cannot receive direct HP heals; recovers HP on each attack hit (heal-on-hit); Tenacity buff: ATK/DEF scale up as HP drops | Hellagur, Skadi-alt (Skadi the Corrupting Heart), Akafuyu |
| `SPEC_EXECUTOR` | Very low redeployment timer (~10s); powerful opening skill that decays over time; designed for redeploy-loop tactics | Kafka (partial — has test but archetype behavior not enforced), Robin, Aosta |
| `MEDIC_WANDERING` | Removes Elemental Injuries from allies; heals 0-HP-needed allies to clear elemental buildup; low DP cost | Mulberry, Purestream |
| `SUP_BARD` | No attack at all; passive 10% ATK/s healing aura to all allies in range; grants Inspiration flat stat buff | Sora (has data file but archetype logic unimplemented), Cantabile, Hibiscus-alt |
| `SPEC_DOLLKEEPER` | Switch to substitute body on fatal damage (20s); substitute has same stats but cannot block; HP drains over time (needs external healing) | Kal'tsit (generated data file only), Spuria |
| `GUARD_LIBERATOR` | Cannot block or attack when skill is inactive; ATK accumulates passively up to +200% over 40s when skill is off; 2→3 block at E2 | Mountain (has data file; liberator passive ATK ramp not in system) |

### 2.2 Missing Sub-archetypes With No Enum Entry

These exist in the game but are absent from the `RoleArchetype` enum entirely:

| Archetype | Key Mechanic | Notes |
|-----------|-------------|-------|
| `GUARD_EARTHSHAKER` | Attacks deal physical damage to all blocked enemies (like Centurion but focused on choke-point AoE) | Pozemka, Chestnut |
| `GUARD_PRIMAL` | Primal Guard; melee Arts-damage guards with unique talent bonuses | Added post-launch |
| `CASTER_INCANTATION_MEDIC` | (`MEDIC_INCANTATION`) — attacks enemies dealing Arts damage AND heals one ally for 50% damage dealt | Eyjafjalla-alt, Quercus, Hibiscus-alt |
| `MEDIC_CHAIN` | Single-target heal that chains to adjacent allies; jump range = 8-surrounding tiles | Honeyberry, Breeze |
| `DEF_DUELIST` | Block-1 only; very high HP and ATK; attacks ground tile ahead | Tequila, Gummy-alt |
| `DEF_PRIMAL_PROTECTOR` | Builds up Elemental Damage on enemies with skill; also resists elemental damage | Eunectes |
| `SUP_RITUALIST` | Like Decel Binder but applies Elemental Injury buildup on hits | Gnosis-alt, Podenco-alt |
| `SUP_SUMMONER` | Deploys combat tokens that occupy deployment slots; tokens count against unit limit | Ling, Magallan, Mayer — partially scaffolded |
| `SUP_HEXER` | Applies Fragile debuff (all damage taken multiplied); high range; deals meaningful damage | Shamare, Pramanix |
| `VAN_STRATEGIST` | (`VAN_TACTICIAN` is correct for Beanstalk but Strategist is a separate branch) | Texas-alt |
| `SNIPER_SPREADSHOOTER` | AoE physical splash on ground targets from high ground | Vermeil, Vermeil-alt |

---

## 3. Mechanic System Gaps

### 3.1 Elemental Injury System (CRITICAL for accuracy vs. recent content)

**Current state:** `ElementType` enum exists (`NECROSIS`, `EROSION`, `COMBUSTION`), `AttackType.ELEMENTAL` exists, but no system processes elemental buildup, thresholds, or on-proc effects.

**What's needed:**
- Each unit needs an `elemental_hp: dict[ElementType, float]` pool (max 1000 per type)
- On proc (reaching 1000): apply the damage + debuff, then enter 10s immunity window
  - **Combustion** (Burn): 1200 Arts damage + RES -20 for 10s
  - **Erosion** (Corrosion): 800 Physical damage + DEF permanently -100 (stackable)
  - **Necrosis**: 3000 True damage (Freeze-like CC component)
- `MEDIC_WANDERING` archetype is the primary counter — removes elemental buildup from allies
- Without this, operators like Gnosis S2, Podenco S2, Eunectes S3, and the Primal Protector archetype cannot be simulated at all

### 3.2 Bard Archetype Passive Aura (HIGH priority)

**Current state:** `SUP_BARD` is in the enum; Sora has a data file; `targeting_system.py` references bard. But the passive AOE heal-per-second aura is not implemented as a system-level mechanism.

**What's needed:**
- Bard units do not attack at all (no `__target__` set in targeting system)
- Each tick: for every ally in range, heal `bard.effective_atk * 0.10` HP
- Inspiration buff: grant a flat ATK bonus to all allies in range equal to `N` (operator-specific)
- Sora S1/S2: her passive aura is conditional on skill state

### 3.3 Overload Mechanic

**Current state:** Not implemented. The `SkillTrigger` and skill duration logic exists, but no "dual-meter" skill state.

**What's needed:**
- Skills marked as Overload use two stacked duration/ammo meters
- When the remaining duration falls below 50% of total, the skill enters "overloaded" state with boosted effects but incurs a drawback (operator-specific)
- Relevant operators: Surtr S3 (has test — verify if this mechanic is actually exercised), Ascalon

### 3.4 Substitute/Dollkeeper Mechanic

**Current state:** Not implemented (only Kal'tsit's generated data file exists).

**What's needed:**
- When Dollkeeper would die, instead switch to `substitute` state for 20s
- Substitute: same stats, cannot block, HP drains over time
- After 20s, revert to Dollkeeper with full HP and 0 SP
- If substitute is killed, operator is treated as dead (forced redeploy)

### 3.5 Musha Guard Heal-On-Hit + No-External-Heal

**Current state:** Not implemented.

**What's needed:**
- Musha Guards cannot be healed by external medics/allies (bypass restriction)
- On each attack that connects: heal self for `N` HP (operator/skill-dependent value)
- Tenacity: ATK and DEF scale inversely with current HP ratio (stronger when low HP)
- Note: Bard passive aura BYPASSES the no-heal restriction (it's not classified as "direct HP restoration")

### 3.6 Liberator Guard ATK Accumulation

**Current state:** Mountain has a data file and test, but the passive ATK ramp during skill-inactive phases is not enforced by any system.

**What's needed:**
- When skill is inactive: every second, ATK increases by a fixed amount (up to cap of +200% base ATK after ~40s)
- When skill activates: ATK is reset, and the operator begins attacking/blocking again
- This is a time-accumulated passive, not a standard `REGEN`-style status

### 3.7 Executor Specialist Redeploy Loop

**Current state:** Kafka has tests but the Executor archetype trait (short redeploy timer, opening-skill-decay) is not enforced at the system level — any operator can currently be redeployed.

**What's needed:**
- Track per-operator `redeploy_timer` (default 70s game standard; Executor branch gets 10s)
- `SPEC_EXECUTOR` trait: timer = 10s after retreat; skill starts at full power and decays
- This affects DPS calculations significantly for operators like Kafka and Robin

---

## 4. Common Fan Simulator Accuracy Issues

Based on research into Arknights mechanics documentation and simulator design patterns, the most common accuracy failures are:

### 4.1 Tick Rate vs. Game Real Rate (MEDIUM risk in current codebase)
- The game runs at 30 ticks/second; this simulator runs at 10 ticks/second (10 Hz, `TICK_RATE = 10`)
- ATK interval rounding happens at 30fps in the real game: `interval_in_ticks = round(base_interval * 30) / 30`
- At 10 Hz, sub-frame effects (e.g., 0.05s status tick interactions) are rounded differently
- **Impact:** ASPD buffs that push attack intervals below 0.1s will be handled differently; extreme cases like Surtr S3 burst may drift

### 4.2 Attack Interval Wind-Up/Wind-Down Phase
- The real game has three attack phases: Wind-up (animation start), Launch (damage dealt), Wind-down (cooldown until next Wind-up)
- Fan simulators typically model only a single `atk_cd` value — this is correct for steady state but misses first-attack latency
- **Current codebase risk:** `u.atk_cd = u.current_atk_interval` after each attack is standard; however, no initial deployment delay is modeled. In practice, operators have a ~0.3s first-attack wind-up after deployment.

### 4.3 SP Lockout Window
- After certain SP-granting events (deploy, skill-end), there is a brief SP lockout window where no SP can be gained
- `Ptilopsis` talent (SP aura) has a known lockout interaction — she cannot grant SP during lockout windows
- Current `status_system.py` and `skill_system.py` do not model SP lockout periods

### 4.4 Buff Stacking Order (RATIO vs MULTIPLIER)
- The current `BuffStack` enum correctly distinguishes RATIO (additive %) and MULTIPLIER (multiplicative) stacking
- **Risk:** Multiple operators applying RATIO ATK buffs must be summed before multiplying by the MULTIPLIER chain. If ordering is wrong, the final ATK can over/under-compute by 5-20% in buffed scenarios.
- Verify: Warfarin + Angelina + Sora stacking produces correct final ATK via the formula `[FLOOR(base * stage) * (1 + sum_of_RATIO)] * product_of_MULTIPLIER + FLAT`

### 4.5 Fragile Stacking (Damage Amplification)
- Fragile (and other damage amplification effects) stack multiplicatively with each other: each source multiplies the running total
- Common mistake: treating Fragile as additive. Two 10% Fragile sources should give 1.10 × 1.10 = 1.21×, not 1.20×
- The current `StatusKind.FRAGILE` implementation should be audited for this

### 4.6 Minimum Damage Floor
- Physical damage minimum: `max(5% of final ATK, 1)`
- This prevents DEF-stacking enemies from taking 0 physical damage
- Confirm this floor is applied in `take_physical()` in `unit_state.py`

### 4.7 Accuracy/Evasion Miss Mechanic
- Introduced in Operation Lucent Arrowhead (late 2023): enemies can have Accuracy debuffs applied
- A miss does NOT prevent status effects from being applied (only damage is avoided)
- A miss does NOT trigger defensive SP recovery
- A miss does prevent reflect-damage talents from triggering
- This is a newer mechanic; current simulator likely ignores it entirely (acceptable for pre-Arrowhead content)

---

## 5. Recommended Implementation Priority

| Priority | Item | Rationale |
|----------|------|-----------|
| P1 | **Elemental Injury system** (full: buildup → proc → immunity) | Enables Gnosis, Podenco, Eunectes, all Primal operators, and future content |
| P2 | **Bard passive aura + Inspiration buff** | Sora data exists; enables support-focused team compositions |
| P3 | **GUARD_MUSHA** mechanics (no-heal, heal-on-hit, Tenacity) | Hellagur/Skadi-alt are high-value meta operators; missing archetype |
| P4 | **SP lockout window** | Fixes Ptilopsis interactions; affects any speedrun/min-cycle calculation |
| P5 | **SPEC_EXECUTOR redeploy timer** | Kafka is already tested; just needs system-level enforcement |
| P6 | **Liberator Guard ATK ramp** | Mountain test exists; passive ATK accumulation not enforced |
| P7 | **Dollkeeper substitute** | Kal'tsit is meta; complex but well-specified mechanic |
| P8 | **SUP_HEXER archetype** (Fragile aura + damage) | Shamare, Pramanix — debuffer archetype currently unimplemented |
| P9 | **MEDIC_INCANTATION** (damage → heal conversion) | Eyjafjalla-alt is a popular operator; unique mechanic |
| P10 | **MEDIC_CHAIN** (bouncing heal) | Honeyberry/Breeze — support medic tier |
| P11 | **Overload mechanic** (dual skill meter) | Surtr S3 partial; needed for future Ascalon-type operators |
| P12 | **Accuracy/Evasion miss system** | Only relevant for post-Arrowhead content; not breaking for current test suite |
| P13 | **Tick rate accuracy** (30Hz rounding vs 10Hz) | Fine-grained correctness; low user-visible impact except extreme ASPD scenarios |

---

## 6. Missing Archetype Enums to Add

These `RoleArchetype` values should be added to `core/types.py`:

```python
# Guard additional
GUARD_EARTHSHAKER = "guard_earthshaker"    # 震地者 (multi-target same-block AoE)
GUARD_PRIMAL = "guard_primal"              # 蛮兵 (primal Arts Guard)
GUARD_SOLOBLADE = "guard_soloblade"        # 独剑者 (Młynar)

# Defender additional  
DEF_DUELIST = "def_duelist"               # 决斗者 (block-1, high HP/ATK)
DEF_PRIMAL = "def_primal"                 # 原始卫士 (elemental buildup)

# Sniper additional
SNIPER_CLOSERANGE = "sniper_closerange"   # 速射手 close-range subtype
SNIPER_SPREADSHOOTER = "sniper_spreadshooter"  # 散射手 (Vermeil)

# Caster additional
CASTER_MECH_ACCORD = "caster_mech_accord"  # 机械术师 (Mostima-alt type)
CASTER_PRIMAL = "caster_primal"            # 秘源术师

# Medic additional
MEDIC_INCANTATION = "medic_incantation"   # 秘咒医疗 (damage-heal hybrid)
MEDIC_CHAIN = "medic_chain"               # 链式医疗

# Supporter additional
SUP_RITUALIST = "sup_ritualist"           # 秘仪师 (elemental buildup debuff)
SUP_ABJURER = "sup_abjurer"              # already in enum — verify implementation

# Vanguard additional
VAN_STRATEGIST = "van_strategist"         # 战略家 (Texas-alt)
```

---

## 7. Sources

- [Damage - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Damage)
- [Elemental Damage - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Damage/Elemental)
- [Elemental Injury - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Elemental_Injury)
- [Skill Point - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Skill_Point)
- [Overcharge - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Overcharge)
- [Musha Guard | Arknights Wiki | Fandom](https://arknights.fandom.com/wiki/Guard/Musha)
- [Dollkeeper Specialist - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Specialist/Dollkeeper)
- [Liberator Guard - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Guard/Liberator)
- [Bard Supporter - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Supporter/Bard)
- [Wandering Medic - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Medic/Wandering)
- [Incantation Medic - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Medic/Incantation)
- [Ritualist Supporter - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Supporter/Ritualist)
- [Class - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Class)
- [Accuracy - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Accuracy)
- [Attack interval - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Attribute/Attack_interval)
- [Arknights Mechanics: Behind the Numbers - Attack Speed | GamePress](https://ak.gamepress.gg/core-gameplay/arknights-mechanics-behind-numbers-attack-speed)
- [Buff - Arknights Terra Wiki](https://arknights.wiki.gg/wiki/Buff)
