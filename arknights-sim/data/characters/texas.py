"""Texas — 6* Vanguard (Pioneer archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent: Tactical Delivery (E2) — grants +2 DP at operation start when in squad.
  (NOT DP on kill; Pioneer class trait is just Block 2. Charger archetype gets DP on kill.)
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)
from core.systems.talent_registry import register_talent
from data.characters.generated.texas import make_texas as _base_stats


PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_TACTICAL_DELIVERY_TAG = "texas_tactical_delivery"


def _on_battle_start(world, unit) -> None:
    world.global_state.refund_dp(2)  # E2 rank: +2 DP at operation start


register_talent(_TACTICAL_DELIVERY_TAG, on_battle_start=_on_battle_start)


def make_texas() -> UnitState:
    """Texas E2 max, trust 100. Tactical Delivery: +2 DP at operation start."""
    op = _base_stats()
    op.name = "Texas"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.range_shape = PIONEER_RANGE
    op.block = 2
    op.cost = 13
    op.talents = [TalentComponent(
        name="Tactical Delivery",
        behavior_tag=_TACTICAL_DELIVERY_TAG,
    )]
    return op
