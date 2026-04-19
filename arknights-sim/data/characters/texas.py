"""Texas — 6* Vanguard (Pioneer archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Trait: Vanguard Pioneer — generates 1 DP when killing an enemy.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from core.systems.talent_registry import register_talent
from data.characters.generated.texas import make_texas as _base_stats


PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_DP_ON_KILL_TAG = "vanguard_pioneer_dp_on_kill"


def _on_kill(world, killer, killed) -> None:
    if killed.faction.value == "enemy":
        world.global_state.refund_dp(1)


register_talent(_DP_ON_KILL_TAG, on_kill=_on_kill)


def make_texas() -> UnitState:
    """Texas E2 max, trust 100. Pioneer DP-on-kill trait wired."""
    op = _base_stats()
    op.name = "Texas"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.range_shape = PIONEER_RANGE
    op.block = 2
    op.cost = 13
    op.talents = [TalentComponent(
        name="Pioneer (DP on kill)",
        behavior_tag=_DP_ON_KILL_TAG,
    )]
    return op
