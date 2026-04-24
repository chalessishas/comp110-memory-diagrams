"""Quercu (Quercus 桂枝) — 5★ Supporter (Bard).

S1: sp_cost=20, initial_sp=10, duration=20s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=30, initial_sp=15, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.quercu import make_quercu as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "quercu_s1"; _S1_DURATION = 20.0
_S2_TAG = "quercu_s2"; _S2_DURATION = 25.0

def make_quercu(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Quercus"
    op.archetype = RoleArchetype.SUP_BARD
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Quercus S1", slot="S1", sp_cost=20, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Quercus S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
