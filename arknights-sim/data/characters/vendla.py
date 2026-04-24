"""Vendla — stub operator.

S1: sp_cost=10, initial_sp=5, duration=5.0s, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=15.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.vendla import make_vendla as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "vendla_s1"; _S1_DURATION = 5.0
_S2_TAG = "vendla_s2"; _S2_DURATION = 15.0

def make_vendla(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Vendla"
    op.archetype = RoleArchetype.MEDIC_INCANTATION
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Vendla S1", slot="S1", sp_cost=10, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Vendla S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
