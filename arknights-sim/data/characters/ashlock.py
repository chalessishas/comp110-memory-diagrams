"""Ashlock (灰毫) — 5* Defender (Fortress archetype).

Fortress class trait: attacks all enemies in range when NOT blocking (ranged physical AoE);
when blocking, attacks single target (melee mode). Identical archetype behavior to Horn.

Range shapes follow the same pattern as Horn (ArknightsGameData Fortress Defender grid):
  - Ranged: 3-tile forward line + side tiles
  - Melee:  operator tile + 1 tile forward
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Faction, Profession, RoleArchetype
from data.characters.generated.ashlok import make_ashlok as _base_stats


_RANGED_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1),
))

_MELEE_RANGE = RangeShape(tiles=(
    (0, 0), (1, 0),
))


def make_ashlock() -> UnitState:
    """Ashlock E2 max. Fortress class trait: ranged AoE ↔ melee single based on blocking state."""
    op = _base_stats()
    op.name = "Ashlock"
    op.archetype = RoleArchetype.DEF_FORTRESS
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.block = 3
    op.cost = 27

    op.range_shape = _RANGED_RANGE
    op._melee_range = _MELEE_RANGE

    return op
