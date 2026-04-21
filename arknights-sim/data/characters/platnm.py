"""Platinum (白金) — 5* Sniper (Marksman archetype).

S1 "ATK Up γ" (攻击力强化·γ型): ATK +100% for 30s.
  sp_cost=30, initial_sp=15, MANUAL, AUTO_TIME.

S2 "Pegasus Vision" (天马视域): ATK +100%, ASPD −20 (permanent toggle).
  sp_cost=50, initial_sp=0, AUTO, instant (duration=0). Fires once and stays.
  Slows attack speed but hits harder — net DPS gain.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import (
    UnitState, SkillComponent, Buff, RangeShape,
)
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.platnm import make_platnm as _base_stats


MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

# --- S1: ATK Up γ ---
_S1_TAG = "platnm_s1_atk_up"
_S1_ATK_RATIO = 1.00
_S1_BUFF_TAG = "platnm_s1_atk"
_S1_DURATION = 30.0

# --- S2: Pegasus Vision (instant permanent toggle) ---
_S2_TAG = "platnm_s2_pegasus_vision"
_S2_ATK_RATIO = 1.00      # ATK +100% (permanent)
_S2_ASPD_DELTA = -20.0    # ASPD −20 (permanent penalty, slower but harder)
_S2_ATK_BUFF_TAG = "platnm_s2_atk"
_S2_ASPD_BUFF_TAG = "platnm_s2_aspd"


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Platinum S1 ATK Up γ — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    # Remove any existing S2 buffs before applying (idempotent)
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG)]
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_DELTA, source_tag=_S2_ASPD_BUFF_TAG,
    ))
    world.log(f"Platinum S2 Pegasus Vision — ATK+{_S2_ATK_RATIO:.0%}, ASPD{_S2_ASPD_DELTA:+.0f} (permanent)")


# S2 is instant (duration=0): on_end is never called, buffs persist permanently.
register_skill(_S2_TAG, on_start=_s2_on_start)


def make_platnm(slot: str = "S2") -> UnitState:
    """Platinum E2 max. S1: ATK+100%/30s MANUAL. S2: permanent ATK+100% ASPD-20 AUTO."""
    op = _base_stats()
    op.name = "Platinum"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MARKSMAN_RANGE

    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ",
            slot="S1",
            sp_cost=30,
            initial_sp=15,
            duration=_S1_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL,
            requires_target=False,
            behavior_tag=_S1_TAG,
        )
        op.skill.sp = float(op.skill.initial_sp)
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Pegasus Vision",
            slot="S2",
            sp_cost=50,
            initial_sp=0,
            duration=0.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
