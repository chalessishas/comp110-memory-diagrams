"""Dobermann (杜宾) — 5★ Instructor Guard.

S1 "Power Strike β": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack → 200% ATK; single-hit power-shot not modeled — stub).
S2 "Spur": sp_cost=35, initial_sp=17, duration=25s, AUTO_TIME, MANUAL
  (party ATK+23% + ASPD+13 within range; party-wide multi-unit buff not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.doberm import make_doberm as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "doberm_s1_power_strike"
_S1_DURATION = 0.0

_S2_TAG = "doberm_s2_spur"
_S2_DURATION = 25.0


def make_doberm(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Dobermann"
    op.archetype = RoleArchetype.GUARD_INSTRUCTOR
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Power Strike β", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Spur", slot="S2", sp_cost=35, initial_sp=17,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
