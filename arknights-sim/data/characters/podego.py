"""Podego (Podenco 波登可) — 4★ Supporter (Decel).

S1: sp_cost=25, initial_sp=10, duration=30s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=23, initial_sp=10, duration=6s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.podego import make_podego as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "podego_s1"; _S1_DURATION = 30.0
_S2_TAG = "podego_s2"; _S2_DURATION = 6.0

def make_podego(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Podenco"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Podenco S1", slot="S1", sp_cost=25, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Podenco S2", slot="S2", sp_cost=23, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
