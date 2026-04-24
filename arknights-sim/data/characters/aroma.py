"""Aroma (阿罗玛) — 5★ Caster (Mystic).

S1: sp_cost=6, initial_sp=4, duration=10s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=50, initial_sp=25, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.aroma import make_aroma as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "aroma_s1"
_S1_DURATION = 10.0

_S2_TAG = "aroma_s2"
_S2_DURATION = 25.0


def make_aroma(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Aroma"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Aroma S1", slot="S1", sp_cost=6, initial_sp=4,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Aroma S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
