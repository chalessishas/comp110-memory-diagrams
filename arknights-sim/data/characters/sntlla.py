"""Sntlla (Sntlla) — stub operator.

S1: sp_cost=10, initial_sp=0, duration=0.0s, AUTO_TIME, AUTO (stub).
S2: sp_cost=35, initial_sp=18, duration=15.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.sntlla import make_sntlla as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "sntlla_s1"; _S1_DURATION = 0.0
_S2_TAG = "sntlla_s2"; _S2_DURATION = 15.0

def make_sntlla(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Sntlla"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Sntlla S1", slot="S1", sp_cost=10, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Sntlla S2", slot="S2", sp_cost=35, initial_sp=18,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
