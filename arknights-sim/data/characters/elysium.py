"""Elysium — 6* Vanguard (Standard Bearer archetype).

Talent "Standard Instruction" (E2): All deployed Vanguard operators gain +0.3 SP/s.
  Applies to all SP-using Vanguards including Elysium himself.

S1 "Support γ": 18 DP over 8s while not blocking (block=0 during skill).
  sp_cost=35, initial_sp=10 (base/M0), duration=8s, requires_target=False.
  DP rate: 18/8 = 2.25 DP/s — higher than Myrtle S1 (1.75 DP/s).

Arknights wiki: Standard Bearer stops blocking during skill activation.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    Faction, Profession, RoleArchetype, SPGainMode, SkillTrigger,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.elysm import make_elysm as _base_stats


STANDARD_BEARER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Standard Instruction ---
_TALENT_TAG = "elysium_standard_instruction"
_TALENT_SP_RATE = 0.3           # SP/s to all deployed Vanguards (E2 max)
_TALENT_SP_FRAC = "_elysium_talent_sp_frac"


def _talent_on_tick(world, carrier, dt: float) -> None:
    frac = getattr(carrier, _TALENT_SP_FRAC, 0.0) + _TALENT_SP_RATE * dt
    sp_bonus = frac
    if sp_bonus < 0.01:
        setattr(carrier, _TALENT_SP_FRAC, sp_bonus)
        return

    now = world.global_state.elapsed
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        if ally.profession != Profession.VANGUARD:
            continue
        sk = ally.skill
        if sk is None or sk.active_remaining > 0:
            continue
        if now < sk.sp_lockout_until:
            continue
        sk.sp = min(sk.sp + sp_bonus, float(sk.sp_cost))
    setattr(carrier, _TALENT_SP_FRAC, 0.0)


register_talent(_TALENT_TAG, on_tick=_talent_on_tick)


# --- S1 ---
_S1_TAG = "elysium_s1_support_gamma"
_S1_DP_RATE = 18.0 / 8.0      # 2.25 DP/s over 8s
_S1_DP_FRAC_ATTR = "_elysium_s1_dp_frac"


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


def make_elysium(slot: str = "S1") -> UnitState:
    """Elysium E2 max. Talent: +0.3 SP/s to all Vanguards. S1 Support γ: 18 DP / 8s."""
    op = _base_stats()
    op.name = "Elysium"
    op.archetype = RoleArchetype.VAN_STANDARD_BEARER
    op.range_shape = STANDARD_BEARER_RANGE
    op.block = 1
    op.cost = 11
    op.talents = [TalentComponent(name="Standard Instruction", behavior_tag=_TALENT_TAG)]

    if slot == "S1":
        op.skill = SkillComponent(
            name="Support γ",
            slot="S1",
            sp_cost=35,
            initial_sp=10,
            duration=8.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )

    return op
