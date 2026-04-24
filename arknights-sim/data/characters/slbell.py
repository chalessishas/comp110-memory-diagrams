"""Slbell (Silver Bell 银铃) — 4★ Supporter (Decel).

S1: sp_cost=15, initial_sp=8, duration=0s, AUTO_TIME, AUTO (stub).
S2: sp_cost=25, initial_sp=12, duration=10s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.slbell import make_slbell as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "slbell_s1"; _S1_DURATION = 0.0
_S2_TAG = "slbell_s2"; _S2_DURATION = 10.0

def make_slbell(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Silver Bell"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Silver Bell S1", slot="S1", sp_cost=15, initial_sp=8,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Silver Bell S2", slot="S2", sp_cost=25, initial_sp=12,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
