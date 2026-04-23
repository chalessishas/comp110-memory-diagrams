"""Ash (灰烬) — 6★ Marksman Sniper (Rainbow Six collab).

S1 "Supporting Fire": sp_cost=45, initial_sp=0, toggle, AUTO_TIME, AUTO
  (ATK+15% + double-hit; double-hit not modeled — stub).
S2 "Assault Tactics": sp_cost=25, initial_sp=0, ammo toggle, AUTO_ATTACK, MANUAL
  (atk interval ×0.2, 31-bullet ammo pool; ammo system not modeled — stub).
S3 "Breaching Rounds": sp_cost=25, initial_sp=0, instant 2-use, AUTO_ATTACK, MANUAL
  (300%/400% ATK projectile+AoE; limited-use AoE not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.ash import make_ash as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "ash_s1_supporting_fire"
_S1_DURATION = 0.0

_S2_TAG = "ash_s2_assault_tactics"
_S2_DURATION = 0.0

_S3_TAG = "ash_s3_breaching_rounds"
_S3_DURATION = 0.0


def make_ash(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Ash"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Supporting Fire", slot="S1", sp_cost=45, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Assault Tactics", slot="S2", sp_cost=25, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Breaching Rounds", slot="S3", sp_cost=25, initial_sp=0,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
