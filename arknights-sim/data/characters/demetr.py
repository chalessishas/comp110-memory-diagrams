"""Bellone (贝洛内) — 6★ Guard (Fighter).

S1 "Don's Ease": sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack hits twice at 250% ATK — double-hit stub).
S2 "Consigliere's Schemes": sp_cost=22, initial_sp=14, duration=22s, AUTO_TIME, MANUAL
  (range expands, ASPD+80, 3-target 200% ATK, talent-stack slow — stub).
S3 "Settling Old Scores": sp_cost=35, initial_sp=27, duration=30s, AUTO_TIME, MANUAL
  (ATK+170%, ASPD+50, 50% bonus proc, survive-lethal mechanic — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.demetr import make_demetr as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "demetr_s1_dons_ease"
_S1_DURATION = 0.0

_S2_TAG = "demetr_s2_consiglieres_schemes"
_S2_DURATION = 22.0

_S3_TAG = "demetr_s3_settling_old_scores"
_S3_DURATION = 30.0


def make_demetr(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Bellone"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Don's Ease", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Consigliere's Schemes", slot="S2", sp_cost=22, initial_sp=14,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Settling Old Scores", slot="S3", sp_cost=35, initial_sp=27,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
