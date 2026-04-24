"""Beanstalk (赤豆) — 4★ Vanguard (Tactician).

S1 "Sentinel Command": sp_cost=34, initial_sp=11, duration=0s (DP generation, stub).

S2 "'Everyone Together!'": sp_cost=44, initial_sp=14, duration=15s (complex rally, stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.bstalk import make_bstalk as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "bstalk_s1_sentinel_command"
_S1_DURATION = 0.0

_S2_TAG = "bstalk_s2_everyone_together"
_S2_DURATION = 15.0


def make_bstalk(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Bstalk"
    op.archetype = RoleArchetype.VAN_TACTICIAN
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Sentinel Command", slot="S1", sp_cost=34, initial_sp=11,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="'Everyone Together!'", slot="S2", sp_cost=44, initial_sp=14,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
