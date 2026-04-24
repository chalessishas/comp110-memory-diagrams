"""Hung (吽) — 5★ Defender (Protector) (char_226).

S1: sp_cost=5, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2: sp_cost=55, initial_sp=30, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.hmau import make_hmau as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))
_S1_TAG = "hmau_s1"; _S1_DURATION = 0.0
_S2_TAG = "hmau_s2"; _S2_DURATION = 30.0

def make_hmau(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Hung"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Hung S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Hung S2", slot="S2", sp_cost=55, initial_sp=30,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
