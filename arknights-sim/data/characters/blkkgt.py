"""Degenbrecher (锏) — 6★ Swordmaster Guard.

S1 "Pure Force": sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack 190% ATK to ≤6 ground enemies twice; multi-target double-hit — stub).
S2 "Silent Derision": sp_cost=12, initial_sp=5, instant, AUTO_ATTACK, MANUAL
  (2-3 slashes 280% ATK to ≤5 ground enemies, 2 charges; conditional count + multi-slash — stub).
S3: estimated sp_cost=70, initial_sp=35, duration=20s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.blkkgt import make_blkkgt as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "blkkgt_s1_pure_force"
_S1_DURATION = 0.0

_S2_TAG = "blkkgt_s2_silent_derision"
_S2_DURATION = 0.0

_S3_TAG = "blkkgt_s3"
_S3_DURATION = 20.0


def make_blkkgt(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Degenbrecher"
    op.archetype = RoleArchetype.GUARD_SWORDMASTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Pure Force", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Silent Derision", slot="S2", sp_cost=12, initial_sp=5,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Degenbrecher S3", slot="S3", sp_cost=70, initial_sp=35,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
