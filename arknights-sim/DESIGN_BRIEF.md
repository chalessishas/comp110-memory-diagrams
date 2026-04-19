# Arknights Simulator — Design Brief

Pure-Python, no-UI combat simulator for Arknights mechanics. Goal: faithful tick-based battle simulation with verified damage formulas, deployable operators, and stage scripting.

## Tech Stack

- **Python 3.9+**, standard library only + `pyyaml` for stage data
- No GUI, no web server — CLI entry point + structured event log output
- Testable via `pytest` with deterministic seeded randomness

## Architecture: 6 Subsystems

```
arknights-sim/
├── core/
│   ├── entity.py       # Base Entity (HP, ATK, DEF, RES, block, range)
│   ├── operator.py     # Operator(Entity) — deploy, retreat, skills
│   ├── enemy.py        # Enemy(Entity) — pathing, aggro, traits
│   ├── map.py          # Grid, tiles, elevation, deployment zones
│   └── battle.py       # Tick loop, win/loss conditions, event log
├── skills/
│   └── triggers.py     # SkillTrigger: manual / auto-recover / auto-passive
├── stages/
│   └── loader.py       # Load YAML → Stage spec
├── data/
│   ├── operators/      # One YAML per operator
│   └── stages/         # One YAML per stage
├── cli.py              # python -m arknights_sim <stage>
└── tests/
```

## Damage Formula

```
Physical DMG = ATK × multiplier − DEF       (min = ATK × 0.05, i.e. 5% floor)
Magic DMG    = ATK × multiplier × (1 − RES/100)

Block:  enemy is blocked if operator.block_count > 0
Heal:   healer ATK → direct HP restore (no DEF/RES)
```

The 5% minimum ensures no attack ever deals 0, matching game behaviour.

## Tick Loop (10 Hz)

```python
TICK_RATE = 10  # ticks per second

while not battle.is_over():
    battle.tick()          # advance 0.1s
    for entity in entities:
        entity.update(dt=0.1)   # cooldowns, skill timers
    battle.resolve_attacks()
    battle.check_conditions()
```

## Enemy Pathfinding / Aggro (Strategy Pattern)

```python
class AggroStrategy:
    def select_target(self, enemy, operators) -> Optional[Operator]: ...

class BlockingFirst(AggroStrategy):   # prefer operators that are blocking
class LowestHP(AggroStrategy):        # ignore block, attack lowest HP
class ClosestToGoal(AggroStrategy):   # ignore operators, rush goal
```

Default: `BlockingFirst`. Trait enemies (e.g., Stealthy) override.

## Skill Trigger Types

| Type | Trigger condition |
|------|------------------|
| `manual` | User (or AI) activates when SP full |
| `auto_recover` | Activates automatically when SP full |
| `auto_passive` | Always active (passive trait) |

## Stage YAML Format

```yaml
id: main_0-1
name: "Abandoned Frontline"
map:
  width: 8
  height: 5
  tiles:
    - {x: 0, y: 2, type: ground}
    - {x: 7, y: 2, type: goal}
    # ...
enemies:
  - {id: originium_slug, count: 5, interval: 4.0, path: [[0,2],[1,2],...,[7,2]]}
max_lives: 3
```

## Delivery Phases

| Phase | Scope | Acceptance test |
|-------|-------|----------------|
| P1 | Entity + Operator + Enemy + 1v1 battle | Liskarm (DEF=500) tanks 1 Originium Slug to death |
| P2 | Map + Stage loader + single-stage run | main_0-1 clears with 2 ops, 3 lives remaining |
| P3 | Elevation (ranged ops hit over melee), blocked path logic | Exusiai hits enemies blocked by Hoshiguma |
| P4 | Skills (Liskarm SP-link, Hoshiguma shield, Exusiai burst) | Skill effects alter outcome verifiably |
| P5 | CLI + event log (`--log json`) + full test suite | `pytest` green; `python -m arknights_sim data/stages/main_0-1.yaml` runs |

**Estimated scale**: 1,200–1,800 lines across all phases.

## Key Decisions

- **Python not TypeScript** — no UI, numerical simulation, pytest is faster than vitest for pure logic
- **No external libs except pyyaml** — keeps it installable with `pip install pyyaml`, no dependency hell
- **YAML stage data** — human-readable, diff-friendly, easy to add new stages
- **Strategy pattern for aggro** — swappable without touching Entity code
- **5% DMG floor hardcoded** — not configurable, matches Arknights mechanics exactly

## Status

**Design approved, implementation not started.** Run `python -m arknights_sim` once P1 is complete to verify.
