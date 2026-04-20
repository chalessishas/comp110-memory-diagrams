"""Beanstalk (豆苗) — 4* Vanguard (Tactician archetype).

Talent "Professional Breeder" (E1/E2): Metal Crab respawn timer 17s/15s.
  (Summon mechanic not modelled in simulator; talent slot is placeholder.)

S1 "Sentinel Command": Instant, gain +8 DP. sp_cost=34, initial_sp=11, AUTO.
S2 "Everyone Together!": 12 DP drip over 15s, block=0 during skill.
  sp_cost=44, initial_sp=15, AUTO_TIME.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession, RoleArchetype,
    SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.bstalk import make_bstalk as _base_stats


TACTICIAN_RANGE = RangeShape(tiles=((0, 0), (1, 0), (2, 0)))

_BREEDER_TAG = "beanstalk_professional_breeder"

_S1_TAG = "beanstalk_s1_sentinel_command"
_S1_DP = 8

_S2_TAG = "beanstalk_s2_everyone_together"
_S2_DP_TOTAL = 12.0
_S2_DURATION = 15.0
_S2_DP_RATE = _S2_DP_TOTAL / _S2_DURATION   # 0.8 DP/s
_S2_DP_FRAC_ATTR = "_beanstalk_s2_dp_frac"


# Talent: Professional Breeder — summon mechanic not simulated; placeholder registration
register_talent(_BREEDER_TAG)


# --- S1: Sentinel Command ---
def _s1_on_start(world, unit) -> None:
    world.global_state.refund_dp(_S1_DP)


register_skill(_S1_TAG, on_start=_s1_on_start)


# --- S2: Everyone Together! ---
def _s2_on_start(world, unit) -> None:
    unit._beanstalk_s2_saved_block = unit.block
    unit.block = 0
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)


def _s2_on_tick(world, unit, dt: float) -> None:
    frac = getattr(unit, _S2_DP_FRAC_ATTR, 0.0) + _S2_DP_RATE * dt
    dp_grant = int(frac)
    if dp_grant > 0:
        world.global_state.refund_dp(dp_grant)
    setattr(unit, _S2_DP_FRAC_ATTR, frac - dp_grant)


def _s2_on_end(world, unit) -> None:
    unit.block = getattr(unit, "_beanstalk_s2_saved_block", 1)
    setattr(unit, _S2_DP_FRAC_ATTR, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


def make_beanstalk(slot: str = "S2") -> UnitState:
    """Beanstalk E2 max. S1: +8 DP instant. S2: 12 DP/15s drip + block=0."""
    op = _base_stats()
    op.name = "Beanstalk"
    op.archetype = RoleArchetype.VAN_TACTICIAN
    op.profession = Profession.VANGUARD
    op.range_shape = TACTICIAN_RANGE
    op.block = 1
    op.cost = 13
    op.talents = [TalentComponent(name="Professional Breeder", behavior_tag=_BREEDER_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Sentinel Command",
            slot="S1",
            sp_cost=34,
            initial_sp=11,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Everyone Together!",
            slot="S2",
            sp_cost=44,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
