"""Virtuosa (塑心) — 6★ Limited Supporter.

S1 "Golden Ecstasy": sp_cost=6, initial_sp=12, instant (2-charge Necrosis burst, stub).
S2 "Requiem Mass": sp_cost=30, initial_sp=14, 20s (ASPD+45 + multi-target, stub).
S3 "Liberal Tango": sp_cost=60, initial_sp=32, 34s (cross-ally conditional ATK/DEF/HP buff, stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.cello import make_cello as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "cello_s1_golden_ecstasy"
_S2_TAG = "cello_s2_requiem_mass"
_S2_DURATION = 20.0
_S3_TAG = "cello_s3_liberal_tango"
_S3_DURATION = 34.0


def make_cello(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Virtuosa"
    op.archetype = RoleArchetype.SUP_HEXER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Golden Ecstasy", slot="S1", sp_cost=6, initial_sp=12,
            duration=0.0, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Requiem Mass", slot="S2", sp_cost=30, initial_sp=14,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Liberal Tango", slot="S3", sp_cost=60, initial_sp=32,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
