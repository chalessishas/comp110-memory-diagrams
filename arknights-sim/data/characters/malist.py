"""Malist (char) — 4★ Caster (Core).

S1: sp_cost=10, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=15s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.malist import make_malist as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "malist_s1"; _S1_DURATION = 0.0
_S2_TAG = "malist_s2"; _S2_DURATION = 15.0

def make_malist(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Malist"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Malist S1", slot="S1", sp_cost=10, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Malist S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
