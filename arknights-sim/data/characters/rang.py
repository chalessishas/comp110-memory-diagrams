"""Ranger (巡林者) — Tutorial Sniper helper. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.rang import make_rang as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))


def make_rang() -> UnitState:
    op = _base_stats()
    op.name = "Ranger"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    return op
