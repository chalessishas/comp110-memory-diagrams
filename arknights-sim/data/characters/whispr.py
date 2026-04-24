"""Whispr — 5★ Medic (MEDIC_ST).

S1: sp_cost=15, initial_sp=8, duration=0.0s, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=10.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.whispr import make_whispr as _base_stats

OP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "whispr_s1"; _S1_DURATION = 0.0
_S2_TAG = "whispr_s2"; _S2_DURATION = 10.0

def make_whispr(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Whispr"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Whispr S1", slot="S1", sp_cost=15, initial_sp=8,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Whispr S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
