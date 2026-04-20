"""Erato (埃拉托) — 5* Sniper (Besieger archetype).

Class trait: Prioritizes attacking heaviest enemy; deals 1.5× ATK to blocked enemies.

Base stats: E2 max, trust 100 (generated/erato.py).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import Profession, RoleArchetype
from data.characters.generated.erato import make_erato as _base_stats

# Standard Besieger Sniper range: 3 forward + flanking tiles
BESIEGER_RANGE_5STAR = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))


def make_erato() -> UnitState:
    """Erato E2 max. Besieger: targets heaviest enemy; 1.5× ATK to blocked enemies."""
    op = _base_stats()
    op.name = "Erato"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.range_shape = BESIEGER_RANGE_5STAR
    op.block = 1
    op.cost = 23
    return op
