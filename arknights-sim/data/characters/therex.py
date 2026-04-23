"""THRM-EX — Special Specialist unit. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.therex import make_therex as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))


def make_therex() -> UnitState:
    op = _base_stats()
    op.name = "THRM-EX"
    op.archetype = RoleArchetype.SPEC_PUSHER
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    return op
