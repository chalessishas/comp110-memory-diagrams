"""Bobbing (波卜) — 5★ Supporter.

S1 "Nonpeaceful Negotiation": sp_cost=10, initial_sp=0, duration=-1 (auto, stub).

S2 "'You Shall Not Pass'": sp_cost=24, initial_sp=10, duration=11s (complex, stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.bobb import make_bobb as _base_stats

CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

_S1_TAG = "bobb_s1_nonpeaceful"
_S1_DURATION = 0.0

_S2_TAG = "bobb_s2_you_shall_not_pass"
_S2_DURATION = 11.0


def make_bobb(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Bobb"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Nonpeaceful Negotiation", slot="S1", sp_cost=10, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="'You Shall Not Pass'", slot="S2", sp_cost=24, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
