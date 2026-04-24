"""Luton (char) — 6★ Defender (Sentinel).

S1: sp_cost=5, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2: sp_cost=50, initial_sp=25, duration=30s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=65, initial_sp=32, duration=40s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.luton import make_luton as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "luton_s1"; _S1_DURATION = 0.0
_S2_TAG = "luton_s2"; _S2_DURATION = 30.0
_S3_TAG = "luton_s3"; _S3_DURATION = 40.0

def make_luton(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Luton"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Luton S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Luton S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Luton S3", slot="S3", sp_cost=65, initial_sp=32,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
