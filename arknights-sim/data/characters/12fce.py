"""12F — 1★ Caster. No skills at E0 max level.

Module name starts with a digit, so importlib is used for the generated import.
"""
from __future__ import annotations
import importlib
from core.state.unit_state import UnitState, RangeShape
from core.types import AttackType, Profession, RoleArchetype

_gen = importlib.import_module('data.characters.generated.12fce')
_base_stats = _gen.make_12fce

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))


def make_12fce() -> UnitState:
    op = _base_stats()
    op.name = "12F"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    return op
