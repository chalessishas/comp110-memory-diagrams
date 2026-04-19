"""Angelina — 6* Supporter (Decel Binder archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent: slow on basic attack — not yet wired (needs status-on-hit hook).
S3 All for One: team ATK/ASPD buff aura — not yet wired.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from data.characters.generated.angelina import make_angelina as _base_stats


# Decel Supporter standard range: wide cross (4 tiles forward + laterals)
DECEL_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, 1), (2, 1), (1, -1), (2, -1),
))


def make_angelina() -> UnitState:
    """Angelina E2 max, trust 100. Base stats from akgd."""
    op = _base_stats()
    op.name = "Angelina"
    op.archetype = RoleArchetype.SUP_DECEL
    op.range_shape = DECEL_RANGE
    op.cost = 27
    return op
