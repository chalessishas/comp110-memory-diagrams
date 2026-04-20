"""Robrta (罗比菈塔) — 5★ Specialist (Merchant archetype).

SPEC_MERCHANT trait: Can be deployed even when DP is insufficient; deployment
  costs DP (may result in negative DP). Represented here by archetype label;
  the DP-debt mechanic lives in the deployment layer.

Talent "Keen Bargain": While deployed, Robrta passively generates DP at
  _TALENT_DP_RATE per second — representing the merchant's constant resource
  extraction from the battlefield.

S2 "Trade Secrets": 20s duration. ATK +25%; DP generation rate increases to
  _S2_DP_RATE per second during skill.
  sp_cost=20, initial_sp=10, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100, char_484_robrta):
  HP=2470, ATK=570, DEF=450, RES=0, atk_interval=1.5, block=2.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.robrta import make_robrta as _base_stats


MERCHANT_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# Talent: Keen Bargain — passive DP generation
_TALENT_TAG = "robrta_keen_bargain"
_TALENT_DP_RATE = 0.5           # 0.5 DP/s while deployed
_TALENT_DP_FRAC_ATTR = "_robrta_dp_frac"

# S2: Trade Secrets
_S2_TAG = "robrta_s2_trade_secrets"
_S2_ATK_RATIO = 0.25
_S2_ATK_BUFF_TAG = "robrta_s2_atk"
_S2_DP_RATE = 2.0               # 2 DP/s during S2
_S2_DP_FRAC_ATTR = "_robrta_s2_dp_frac"
_S2_DURATION = 20.0


def _talent_on_tick(world, carrier: UnitState, dt: float) -> None:
    frac = getattr(carrier, _TALENT_DP_FRAC_ATTR, 0.0) + _TALENT_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(carrier, _TALENT_DP_FRAC_ATTR, frac - gained)


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    setattr(carrier, _S2_DP_FRAC_ATTR, 0.0)


def _s2_on_tick(world, carrier: UnitState, dt: float) -> None:
    frac = getattr(carrier, _S2_DP_FRAC_ATTR, 0.0) + _S2_DP_RATE * dt
    gained = int(frac)
    if gained > 0:
        world.global_state.refund_dp(gained)
    setattr(carrier, _S2_DP_FRAC_ATTR, frac - gained)


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ATK_BUFF_TAG]
    setattr(carrier, _S2_DP_FRAC_ATTR, 0.0)


register_skill(_S2_TAG, on_start=_s2_on_start, on_tick=_s2_on_tick, on_end=_s2_on_end)


def make_robrta(slot: str = "S2") -> UnitState:
    """Robrta E2 max. SPEC_MERCHANT: passive DP gen (talent) + boosted DP gen + ATK during S2."""
    op = _base_stats()
    op.name = "Robrta"
    op.archetype = RoleArchetype.SPEC_MERCHANT
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.attack_range_melee = True
    op.range_shape = MERCHANT_RANGE
    op.block = 2
    op.cost = 17

    op.talents = [TalentComponent(name="Keen Bargain", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Trade Secrets",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    return op
