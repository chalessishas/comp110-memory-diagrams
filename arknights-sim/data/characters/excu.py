"""Executor (送葬人) — 5★ Marksman Sniper.

S1 "Snipe": sp_cost=2, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (2-charge power shot 200% ATK; single-hit power-shot not modeled — stub).
S2 "Execute": sp_cost=40, initial_sp=20, duration=20s, AUTO_TIME, MANUAL
  (ATK+100% on enemies below 30% HP threshold; conditional ATK boost not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.excu import make_excu as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "excu_s1_snipe"
_S1_DURATION = 0.0

_S2_TAG = "excu_s2_execute"
_S2_DURATION = 20.0


def make_excu(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Executor"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Snipe", slot="S1", sp_cost=2, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Execute", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
