"""Night Blade (夜刀) — Tutorial Vanguard helper. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.nblade import make_nblade as _base_stats

PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))


def make_nblade() -> UnitState:
    op = _base_stats()
    op.name = "Night Blade"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = PIONEER_RANGE
    return op
