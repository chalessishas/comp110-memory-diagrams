"""Saria (塞雷娅) — 6★ Guardian Defender.

S1 "Brilliant Concept": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (heals all allies in range; party-wide heal not modeled — stub).
S2 "Calcification": sp_cost=50, initial_sp=25, duration=28s, AUTO_TIME, MANUAL
  (DEF+% + heals allies in range on attack; multi-target heal + DEF buff coupling — stub).
S3 "The Last Stand": sp_cost=60, initial_sp=20, duration=15s, AUTO_TIME, MANUAL
  (ATK+80% + invincibility for 15s; invincibility status not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.demkni import make_demkni as _base_stats

DEFENDER_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "demkni_s1_brilliant_concept"
_S1_DURATION = 0.0

_S2_TAG = "demkni_s2_calcification"
_S2_DURATION = 28.0

_S3_TAG = "demkni_s3_last_stand"
_S3_DURATION = 15.0


def make_demkni(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Saria"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Brilliant Concept", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Calcification", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="The Last Stand", slot="S3", sp_cost=60, initial_sp=20,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
