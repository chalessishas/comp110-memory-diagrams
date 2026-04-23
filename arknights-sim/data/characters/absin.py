"""Absinthe (苦艾) — 5★ Mystic Caster.

S1 "Enforcement Mode": sp_cost=6, initial_sp=3, toggle, AUTO_TIME, AUTO
  (ATK+60% + target-lowest-HP; toggle not modeled — stub).
S2 "Ultimatum": sp_cost=54, initial_sp=19, duration=27s, AUTO_TIME, MANUAL
  (4-hit burst per attack, each 75% ATK; multi-hit not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.absin import make_absin as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "absin_s1_enforcement_mode"
_S1_DURATION = 0.0

_S2_TAG = "absin_s2_ultimatum"
_S2_DURATION = 27.0


def make_absin(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Absinthe"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Enforcement Mode", slot="S1", sp_cost=6, initial_sp=3,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Ultimatum", slot="S2", sp_cost=54, initial_sp=19,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
