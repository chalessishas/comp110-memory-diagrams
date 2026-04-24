"""Aprot2 (暮落) — Defender (char_4025, Arts Protector).

S1: sp_cost=5, initial_sp=0, instant, AUTO_TIME, AUTO (stub).
S2: sp_cost=50, initial_sp=25, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.aprot2 import make_aprot2 as _base_stats

DEF_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 2) for dy in range(-1, 2)
))

_S1_TAG = "aprot2_s1"
_S1_DURATION = 0.0

_S2_TAG = "aprot2_s2"
_S2_DURATION = 25.0


def make_aprot2(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Aprot2"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.ARTS
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Aprot2 S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Aprot2 S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
