# Arknights ECS Simulator — Mechanics Gaps Research
**Generated**: 2026-04-19 19:37:15  
**Scope**: arknights-sim v2, post-Horn Fortress Defender (P9b complete)

---

## 1. Elysium S1 "Support γ" (Standard Bearer)

- **SP cost**: 35 (SL1) → 26 (M3)  
- **Initial SP**: 10 (SL1) → 15 (M3)  
- **Duration**: 8 s (constant)  
- **DP generated**: **18 DP / 8 s** (vs Myrtle S1: 14 DP / 8 s — Elysium is +4 DP per cast)  
- **Archetype**: Standard Bearer (no attack suppression unlike Myrtle)  
- **ECS gap**: Elysium needs its own `elysium.py`; the drip rate `18/8 = 2.25 DP/s` requires same fractional accumulator pattern as Myrtle S1.

Sources: [Terra Wiki – Elysium](https://arknights.wiki.gg/wiki/Elysium) · [GamePress – Elysium](https://ak.gamepress.gg/operator/elysium)

---

## 2. Myrtle S2 "Healing Wings"

- **SP cost**: 35 (SL1) → 24 (M3)  
- **Initial SP**: 5 → 10  
- **Duration**: **16 s**  
- **DP generated**: **16 DP / 16 s** (1.0 DP/s — lower rate but longer window)  
- **Healing effect**: Heals one adjacent ally per second for 25–50% of Myrtle's ATK (50% at M3). Target = single nearby ally, NOT all adjacent.  
- **Note**: "Tactical Delivery" is the name of **Texas's talent** (+2 DP on battle start). Myrtle S2 is "Healing Wings."  
- **ECS gap**: Requires simultaneous `on_tick` DP drip + `on_tick` heal to most-injured adjacent ally. Combines mechanics from `myrtle.py` S1 and `silence.py` S2.

Sources: [Terra Wiki – Myrtle](https://arknights.wiki.gg/wiki/Myrtle) · [Fandom – Myrtle](https://arknights.fandom.com/wiki/Myrtle)

---

## 3. Vigna (Vanguard Charger) — Talent

Vigna's talent **"Fierce Stabbing"** is a **damage crit chance**, NOT a DP-on-kill mechanic:  
- 10% chance to deal +50% damage on attack (30% during skill active).  
- DP-on-kill is the **Charger archetype trait** (shared by Fang, Vigna, Grani, Popukar). Already implemented in `fang.py` via `vanguard_charger_dp_on_kill`. Vigna reuses the same trait; her unique contribution is the crit talent.  
- **ECS gap**: `vigna.py` needs `vanguard_charger_dp_on_kill` trait + a per-attack random crit modifier. Crit system (`random.random() < 0.10 → atk *= 1.5`) not yet in `combat_system.py`.

Sources: [Terra Wiki – Vigna](https://arknights.wiki.gg/wiki/Vigna) · [Terra Wiki – Charger](https://arknights.wiki.gg/wiki/Vanguard/Charger)

---

## 4. Ashlock (Fortress Defender)

Confirmed **identical archetype** to Horn and Firewhistle: ranged splash AoE when not blocking, single-target melee when blocking. Same `RoleArchetype.DEF_FORTRESS` branch applies with no new ECS work needed.  
- **ECS gap**: `ashlock.py` is a data file only (different range shape, stats). No new systems needed.

Sources: [Terra Wiki – Defender/Fortress](https://arknights.wiki.gg/wiki/Defender/Fortress) · [Sanity;Gone – Ashlock](https://old.sanitygone.help/operators/ashlock)

---

## 5. Healing Over Time (HoT) — Unmodeled Operators

Two passive HoT sources not yet implemented:  
- **Perfumer (Support/Bard)**: Talent passively heals all deployed allies ~10 HP/s (bypasses enmity operators). Unique because it heals units that Medics cannot target.  
- **Angelina S1 "Frigid Breath"**: On-tick slow + gradual ATK buff aura (different from S3 burst already done).  
- **Guardian Defenders** (e.g., Nearl, Gummy): Active skill heals adjacent/all allies, not passive. Already modeled by Silence S2 `on_tick` heal pattern.  
- **ECS gap**: Perfumer's passive aura needs an `on_battle_start` always-active tick heal, distinct from skill-gated HoT.

Sources: [Fandom – Guardian Defender](https://arknights.fandom.com/wiki/Defender/Guardian) · [Terra Wiki – Medic](https://arknights.wiki.gg/wiki/Medic)

---

## 6. Non-Standard Targeting Priorities

Default targeting: highest aggression → closest to exit (path_distance_remaining, now fixed).  
Known deviations:  
- **Deadeye Sniper** archetype: targets **lowest DEF** enemy in range (Exusiai is actually Rapid-Fire, not Deadeye — confirm before implementing).  
- **Ceobe S2 "Really Hot Knives"**: targets **highest DEF** while active.  
- **Ceobe S3 "Really Heavy Spear"**: targets **lowest DEF**, deals Physical.  
- **Absinthe "Enforcement Mode"**: targets **lowest HP%**.  
- **ECS gap**: `targeting_system.py` needs a per-operator `targeting_override` enum (LOWEST_DEF, HIGHEST_DEF, LOWEST_HP_PCT). Deadeye Snipers are archetype-level; Ceobe/Absinthe are skill-level overrides. Two distinct injection points.

Sources: [Fandom – Aggression](https://arknights.fandom.com/wiki/Aggression) · [Fandom – Intermediate Guide](https://arknights.fandom.com/wiki/Intermediate_Guide)

---

## Priority Recommendation

| Priority | Item | New ECS surface |
|----------|------|-----------------|
| P1 | Elysium S1 | Drip rate only (clone Myrtle S1 pattern) |
| P2 | Ashlock data file | Zero new systems |
| P3 | Myrtle S2 | Drip + heal combo tick |
| P4 | Vigna (Charger crit) | New per-attack crit RNG in combat_system |
| P5 | Targeting override enum | Medium — touches targeting_system + each op |
| P6 | Perfumer passive HoT | New always-active aura tick |
