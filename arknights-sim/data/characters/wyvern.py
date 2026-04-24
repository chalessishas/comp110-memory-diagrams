"""Wyvern — 5★ Vanguard (VAN_PIONEER).

S1: sp_cost=15, initial_sp=8, duration=0.0s, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=15.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.wyvern import make_wyvern as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "wyvern_s1"; _S1_DURATION = 0.0
_S2_TAG = "wyvern_s2"; _S2_DURATION = 15.0

def make_wyvern(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Wyvern"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Wyvern S1", slot="S1", sp_cost=15, initial_sp=8,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Wyvern S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
