"""Myrtle — 5* Vanguard (Standard Bearer archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S1 "Tactical Delivery I": 14 DP over 8s while not blocking (block=0 during skill).
  sp_cost=12, initial_sp=6, duration=8s, requires_target=False (fires unconditionally).

Arknights wiki: Standard Bearer stops blocking and attacking during skill activation.
Attack suppression is not modeled yet (low impact — Myrtle's ATK rarely matters).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from data.characters.generated.myrtle import make_myrtle as _base_stats


STANDARD_BEARER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "myrtle_s1_tactical_delivery"
_S1_DP_RATE = 14.0 / 8.0      # 1.75 DP/s over 8s duration
_S1_DP_FRAC_ATTR = "_myrtle_s1_dp_frac"


def _s1_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S1_DP_FRAC_ATTR, 0.0)


def _s1_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S1_DP_FRAC_ATTR, 0.0) + _S1_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S1_DP_FRAC_ATTR, frac - gained)


def _s1_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 1)
    setattr(unit, _S1_DP_FRAC_ATTR, 0.0)


register_skill(_S1_TAG, on_start=_s1_on_start, on_tick=_s1_on_tick, on_end=_s1_on_end)


def make_myrtle(slot: str = "S1") -> UnitState:
    """Myrtle E2 max. S1 Tactical Delivery: 14 DP / 8s, block=0 during skill."""
    op = _base_stats()
    op.name = "Myrtle"
    op.archetype = RoleArchetype.VAN_STANDARD_BEARER
    op.range_shape = STANDARD_BEARER_RANGE
    op.block = 1
    op.cost = 10

    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Delivery I",
            slot="S1",
            sp_cost=12,
            initial_sp=6,
            duration=8.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )

    return op
