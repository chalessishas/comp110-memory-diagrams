"""Gavial the Invincible (百炼嘉维尔) — 6★ Guard (Centurion).

S1: sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=50, initial_sp=25, duration=20s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=70, initial_sp=35, duration=15s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.gvial2 import make_gvial2 as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "gvial2_s1"
_S1_DURATION = 0.0

_S2_TAG = "gvial2_s2"
_S2_DURATION = 20.0

_S3_TAG = "gvial2_s3"
_S3_DURATION = 15.0


def make_gvial2(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Gavial the Invincible"
    op.archetype = RoleArchetype.GUARD_CENTURION
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Gavial the Invincible S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Gavial the Invincible S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Gavial the Invincible S3", slot="S3", sp_cost=70, initial_sp=35,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
