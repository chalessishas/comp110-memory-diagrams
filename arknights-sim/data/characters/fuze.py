"""Fuze (导火索) — Guard/Centurion (char_4126, R6 collab).

S1: sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=50, initial_sp=25, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.fuze import make_fuze as _base_stats

SPEC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_S1_TAG = "fuze_s1"
_S1_DURATION = 0.0

_S2_TAG = "fuze_s2"
_S2_DURATION = 25.0


def make_fuze(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Fuze"
    op.archetype = RoleArchetype.GUARD_CENTURION
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Fuze S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Fuze S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
