"""Horn — 6* Defender (Fortress archetype).

Fortress class trait: attacks all enemies in range when NOT blocking (ranged physical AoE);
when blocking, attacks single target (melee mode). ATK interval switches too:
  - Ranged mode: 2.8s (E2 base)
  - Melee mode:  2.8s (same for Horn, unlike some Fortress variants)

Range shapes (from ArknightsGameData — Defender grid, Horn E2):
  - Ranged (not blocking): cross extending 3 tiles forward + 1 tile side
  - Melee (blocking): operator tile + 1 tile forward (standard defender close range)

Arknights wiki: Fortress Defenders "become a ranged unit dealing group damage when not blocking,
and a melee unit dealing single-target damage when blocking".
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Faction, Profession, RoleArchetype
from data.characters.generated.horn import make_horn as _base_stats

# Ranged mode: 3-tile forward line + 1-tile forward sides (cross shape)
# Horn's actual ranged range: (1,0),(2,0),(3,0),(1,-1),(1,1)
_RANGED_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1),
))

# Melee mode: standard Defender close combat — own tile + 1 forward
_MELEE_RANGE = RangeShape(tiles=(
    (0, 0), (1, 0),
))


def make_horn() -> UnitState:
    """Horn E2 max. Fortress class trait: ranged AoE ↔ melee single based on blocking state."""
    op = _base_stats()
    op.name = "Horn"
    op.archetype = RoleArchetype.DEF_FORTRESS
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.block = 3
    op.cost = 28

    # Ranged mode range is default; targeting_system switches to melee when blocking
    op.range_shape = _RANGED_RANGE
    # Store melee range as secondary attribute for the targeting system to use
    op._melee_range = _MELEE_RANGE

    return op
