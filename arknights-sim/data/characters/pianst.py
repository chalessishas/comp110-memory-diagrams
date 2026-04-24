"""Pianst (char) — 5★ Defender (Arts Protector).

S1: sp_cost=20, initial_sp=10, duration=15s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=45, initial_sp=22, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.pianst import make_pianst as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))
_S1_TAG = "pianst_s1"; _S1_DURATION = 15.0
_S2_TAG = "pianst_s2"; _S2_DURATION = 25.0

def make_pianst(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Pianst"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.ARTS
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Pianst S1", slot="S1", sp_cost=20, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Pianst S2", slot="S2", sp_cost=45, initial_sp=22,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
