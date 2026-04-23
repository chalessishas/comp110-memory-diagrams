"""PhonoR-0 — Robot Supporter unit. No skills."""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype
from data.characters.generated.phonor import make_phonor as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))


def make_phonor() -> UnitState:
    op = _base_stats()
    op.name = "PhonoR-0"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    return op
