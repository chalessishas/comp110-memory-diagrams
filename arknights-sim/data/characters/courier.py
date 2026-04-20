"""Courier (讯使) — 5* Vanguard (Tactician archetype).

Class trait: Tactician Vanguard — no passive DP accumulation; DP via skills.
S1 "Tactical Formation I": Instantly gains 8 DP. sp_cost=25, duration=0 (instant).
S2 "Support Order": 12 DP over 15s (DP drip, block=0 during skill). sp_cost=35.

Talent "Frontline Supply": On deployment, immediately grants 3 DP.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    Profession, RoleArchetype, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.blackd import make_blackd as _base_stats


# --- Talent: Frontline Supply ---
_TALENT_TAG = "courier_frontline_supply"
_DP_GRANT = 3


def _frontline_supply_on_battle_start(world, carrier: UnitState) -> None:
    world.global_state.refund_dp(_DP_GRANT)
    world.log(f"Courier Frontline Supply — +{_DP_GRANT} DP")


register_talent(_TALENT_TAG, on_battle_start=_frontline_supply_on_battle_start)


TACTICIAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- S1: Tactical Formation I — instant 8 DP ---
_S1_TAG = "courier_s1_tactical_formation"
_S1_DP = 8


def _s1_on_start(world, unit) -> None:
    world.global_state.refund_dp(_S1_DP)


register_skill(_S1_TAG, on_start=_s1_on_start)


# --- S2: Support Order — 12 DP over 15s drip ---
_S2_TAG = "courier_s2_support_order"
_S2_DP_RATE = 12.0 / 15.0   # 0.8 DP/s
_S2_DP_FRAC_ATTR = "_courier_s2_dp_frac"


def _s2_on_start(world, unit) -> None:
    unit._saved_block = unit.block
    unit.block = 0
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)


def _s2_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S2_DP_FRAC_ATTR, 0.0) + _S2_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(unit, _S2_DP_FRAC_ATTR, frac - gained)


def _s2_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_saved_block", 2)
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


def make_courier(slot: str = "S1") -> UnitState:
    """Courier E2 max. S1: +8 DP instant; S2: 12 DP / 15s drip, block=0. Talent: +3 DP on deploy."""
    op = _base_stats()
    op.name = "Courier"
    op.archetype = RoleArchetype.VAN_TACTICIAN
    op.profession = Profession.VANGUARD
    op.range_shape = TACTICIAN_RANGE
    op.block = 2
    op.cost = 12
    op.talents = [TalentComponent(name="Frontline Supply", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Formation I",
            slot="S1",
            sp_cost=25,
            initial_sp=10,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Support Order",
            slot="S2",
            sp_cost=35,
            initial_sp=15,
            duration=15.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
