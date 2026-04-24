"""Thorn — stub operator.

S1: sp_cost=5, initial_sp=0, duration=0.0s, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=35, initial_sp=18, duration=20.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.thorn2 import make_thorn2 as _base_stats

SPEC_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "thorn2_s1"; _S1_DURATION = 0.0
_S2_TAG = "thorn2_s2"; _S2_DURATION = 20.0

def make_thorn2(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Thorn"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Thorn S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Thorn S2", slot="S2", sp_cost=35, initial_sp=18,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
