"""Liskarm — 5* Defender (Sentinel archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent: electric arc to attacker on being hit — not yet wired (needs hit_received event).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from data.characters.generated.liskarm import make_liskarm as _base_stats


DEFENDER_MELEE_1 = RangeShape(tiles=((0, 0),))


def make_liskarm() -> UnitState:
    """Liskarm E2 max, trust 100. Base stats from akgd."""
    op = _base_stats()
    op.name = "Liskarm"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.range_shape = DEFENDER_MELEE_1
    op.cost = 21
    return op
