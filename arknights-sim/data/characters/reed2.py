"""Reed2 (Reed the Flame Shadow 焰影苇草) — 6★ Medic (Incantation).

S1: sp_cost=10, initial_sp=5, duration=5s, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=15s, AUTO_TIME, MANUAL (stub).
Note: interval=1.6 (shorter than standard ST medic) signals Incantation archetype.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.reed2 import make_reed2 as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "reed2_s1"; _S1_DURATION = 5.0
_S2_TAG = "reed2_s2"; _S2_DURATION = 15.0

def make_reed2(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Reed the Flame Shadow"
    op.archetype = RoleArchetype.MEDIC_INCANTATION
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Reed the Flame Shadow S1", slot="S1", sp_cost=10, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Reed the Flame Shadow S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
