"""Noir Corne (黑角) — Tutorial Defender helper. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.noirc import make_noirc as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))


def make_noirc() -> UnitState:
    op = _base_stats()
    op.name = "Noir Corne"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    return op
