"""Ebenholz (黑键) — 6★ Phalanx Caster (char_4046).

S1: sp_cost=6, initial_sp=4, duration=15s, AUTO_TIME, AUTO (stub).
S2: sp_cost=60, initial_sp=30, duration=30s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=80, initial_sp=40, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.ebnhlz import make_ebnhlz as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "ebnhlz_s1"
_S1_DURATION = 15.0

_S2_TAG = "ebnhlz_s2"
_S2_DURATION = 30.0

_S3_TAG = "ebnhlz_s3"
_S3_DURATION = 25.0


def make_ebnhlz(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Ebenholz"
    op.archetype = RoleArchetype.CASTER_PHALANX
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Ebenholz S1", slot="S1", sp_cost=6, initial_sp=4,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Ebenholz S2", slot="S2", sp_cost=60, initial_sp=30,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Ebenholz S3", slot="S3", sp_cost=80, initial_sp=40,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
