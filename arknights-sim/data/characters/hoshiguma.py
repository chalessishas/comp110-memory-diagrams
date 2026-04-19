"""Hoshiguma — 6* Defender (Juggernaut archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "Overweight": when HP > 50%, reduce damage taken by 20% (E2 rank).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from data.characters.generated.hoshiguma import make_hoshiguma as _base_stats


DEFENDER_MELEE_BLOCK3 = RangeShape(tiles=((0, 0),))

_OVERWEIGHT_TAG = "hoshiguma_overweight"


def make_hoshiguma() -> UnitState:
    """Hoshiguma E2 max, trust 100. Base stats from akgd; Overweight talent wired."""
    op = _base_stats()
    op.name = "Hoshiguma"
    op.archetype = RoleArchetype.DEF_JUGGERNAUT
    op.range_shape = DEFENDER_MELEE_BLOCK3
    op.cost = 23
    op.talents = [TalentComponent(
        name="Overweight",
        behavior_tag=_OVERWEIGHT_TAG,
        params={"reduction": 0.20, "hp_threshold": 0.5},
    )]
    return op
