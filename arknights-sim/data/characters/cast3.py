"""Castle-3 — Guard drone unit. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.cast3 import make_cast3 as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))


def make_cast3() -> UnitState:
    op = _base_stats()
    op.name = "Castle-3"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    return op
