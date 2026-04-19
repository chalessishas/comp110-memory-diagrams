"""Exusiai — 6* Sniper (Marksman archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Only Orange II" reduces atk_interval — not yet wired.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from data.characters.generated.exusiai import make_exusiai as _base_stats


# Marksman sniper standard range: 3×3 centered forward (simplified)
MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))


def make_exusiai() -> UnitState:
    """Exusiai E2 max, trust 100. Base stats from akgd."""
    op = _base_stats()
    op.name = "Exusiai"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.range_shape = MARKSMAN_RANGE
    op.cost = 16
    return op
