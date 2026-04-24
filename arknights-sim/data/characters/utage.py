"""Utage — stub operator.

S1: sp_cost=5, initial_sp=0, duration=0.0s, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=45, initial_sp=22, duration=20.0s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=60, initial_sp=30, duration=25.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.utage import make_utage as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "utage_s1"; _S1_DURATION = 0.0
_S2_TAG = "utage_s2"; _S2_DURATION = 20.0
_S3_TAG = "utage_s3"; _S3_DURATION = 25.0

def make_utage(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Utage"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Utage S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Utage S2", slot="S2", sp_cost=45, initial_sp=22,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Utage S3", slot="S3", sp_cost=60, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
