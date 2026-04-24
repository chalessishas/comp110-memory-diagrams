"""Frostleaf (霜叶) — 5★ Guard (Swordmaster).

S1 "Frost Tomahawk": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
  Next attack 135% ATK + movement slow; single-hit multiplier not modeled.
S2 "Ice Tomahawk": sp_cost=54, initial_sp=0, duration=25s, AUTO_TIME, MANUAL.
  ASPD+35. Movement slow and bind chance not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.frostl import make_frostl as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "frostl_s1_frost_tomahawk"
_S1_DURATION = 0.0

_S2_TAG = "frostl_s2_ice_tomahawk"
_S2_ASPD_FLAT = 35.0
_S2_BUFF_TAG = "frostl_s2_aspd"
_S2_DURATION = 25.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_FLAT, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Frostleaf S2 — ASPD+{_S2_ASPD_FLAT:.0f}/{_S2_DURATION}s (slow/bind not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_frostl(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Frostleaf"
    op.archetype = RoleArchetype.GUARD_SWORDMASTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Frost Tomahawk", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Ice Tomahawk", slot="S2", sp_cost=54, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
