"""Fang — 4* Vanguard (Charger archetype).

Base stats from ArknightsGameData (E1 max, trust 100).
Charger class trait: gains 1 DP when this unit kills an enemy.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import AttackType, Faction, Profession, RoleArchetype
from core.systems.talent_registry import register_talent
from data.characters.generated.fang import make_fang as _base_stats


CHARGER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_CHARGER_DP_TAG = "vanguard_charger_dp_on_kill"


def _on_kill(world, killer, killed) -> None:
    if killed.faction.value == "enemy":
        world.global_state.refund_dp(1)


register_talent(_CHARGER_DP_TAG, on_kill=_on_kill)


def make_fang() -> UnitState:
    """Fang E1 max. Charger class trait: +1 DP on kill."""
    op = _base_stats()
    op.name = "Fang"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.range_shape = CHARGER_RANGE
    op.block = 2
    op.cost = 11
    op.talents = [TalentComponent(
        name="Charger (DP on kill)",
        behavior_tag=_CHARGER_DP_TAG,
    )]
    return op
