"""Typhon (提丰) — 6* Sniper (Besieger archetype).

Class trait: Prioritizes attacking heaviest enemy; deals 1.5× ATK to blocked enemies.
S1/S2 not implemented (combat-only operator for targeting tests).

Base stats: E2 max, trust 100 (generated/typhon.py).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import Profession, RoleArchetype
from data.characters.generated.typhon import make_typhon as _base_stats

# 6-tile wide forward range: 4 forward + 2 flanking rows
BESIEGER_RANGE_6STAR = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (1, 1), (2, -1), (2, 1), (3, -1), (3, 1),
))


def make_typhon() -> UnitState:
    """Typhon E2 max. Besieger: targets heaviest enemy; 1.5× ATK to blocked enemies."""
    op = _base_stats()
    op.name = "Typhon"
    op.archetype = RoleArchetype.SNIPER_SIEGE
    op.profession = Profession.SNIPER
    op.range_shape = BESIEGER_RANGE_6STAR
    op.block = 1
    op.cost = 24
    return op
