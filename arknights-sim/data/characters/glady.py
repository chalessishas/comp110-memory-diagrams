"""Gladiia (歌蕾蒂娅) — 6★ Specialist (Hookmaster).

S1: sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=50, initial_sp=25, duration=20s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=75, initial_sp=37, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.glady import make_glady as _base_stats

GUARD_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 2) for dy in range(-1, 2)
))

_S1_TAG = "glady_s1"
_S1_DURATION = 0.0

_S2_TAG = "glady_s2"
_S2_DURATION = 20.0

_S3_TAG = "glady_s3"
_S3_DURATION = 30.0


def make_glady(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Gladiia"
    op.archetype = RoleArchetype.SPEC_HOOKMASTER
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Gladiia S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Gladiia S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Gladiia S3", slot="S3", sp_cost=75, initial_sp=37,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
