"""Myrrh (没药) — 4★ Medic (ST).

S1: sp_cost=8, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.myrrh import make_myrrh as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "myrrh_s1"; _S1_DURATION = 0.0
_S2_TAG = "myrrh_s2"; _S2_DURATION = 25.0

def make_myrrh(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Myrrh"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Myrrh S1", slot="S1", sp_cost=8, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Myrrh S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
