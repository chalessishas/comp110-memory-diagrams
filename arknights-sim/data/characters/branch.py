"""Branch — 4★ Defender. No skills at E1 max level."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.branch import make_branch as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))


def make_branch() -> UnitState:
    op = _base_stats()
    op.name = "Branch"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    return op
