"""Warfarin — 5* Medic (Single-target archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S3 ATK Up α adds ATK buff to target ally on heal — not yet wired.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from data.characters.generated.warfarin import make_warfarin as _base_stats


# Medic standard range: 3 tiles in front
MEDIC_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
))


def make_warfarin() -> UnitState:
    """Warfarin E2 max, trust 100. Base stats from akgd; attack_type overridden to HEAL."""
    op = _base_stats()
    op.name = "Warfarin"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.attack_type = AttackType.HEAL
    op.cost = 12
    return op
