"""Friston-3 — Robot Defender unit. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.frston import make_frston as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))


def make_frston() -> UnitState:
    op = _base_stats()
    op.name = "Friston-3"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    return op
