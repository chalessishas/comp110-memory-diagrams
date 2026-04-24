"""Vulcan (火神) — 6★ Defender (Sentinel) (char_163).

S1: sp_cost=5, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2: sp_cost=45, initial_sp=22, duration=40s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=60, initial_sp=30, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.hpsts import make_hpsts as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "hpsts_s1"; _S1_DURATION = 0.0
_S2_TAG = "hpsts_s2"; _S2_DURATION = 40.0
_S3_TAG = "hpsts_s3"; _S3_DURATION = 30.0

def make_hpsts(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Vulcan"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Vulcan S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Vulcan S2", slot="S2", sp_cost=45, initial_sp=22,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Vulcan S3", slot="S3", sp_cost=60, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
