"""CONFESS-47 — 1★ Vanguard. No skills at E0 max level."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.confes import make_confes as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))


def make_confes() -> UnitState:
    op = _base_stats()
    op.name = "CONFESS-47"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    return op
