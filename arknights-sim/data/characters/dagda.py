"""Dagda (达格达) — 5★ Fighter Guard.

S1 "Counter Technique": sp_cost=4, initial_sp=0, instant, AUTO_DEFENSIVE, AUTO
  (on physical hit taken: reduce damage 50% + next attack 180% ATK; reactive proc not modeled — stub).
S2 "Search and Destroy": sp_cost=34, initial_sp=15, duration=15s, AUTO_TIME, MANUAL
  (ATK+28% + double-hit + gang-spirit proc rate; double-hit not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.dagda import make_dagda as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "dagda_s1_counter_technique"
_S1_DURATION = 0.0

_S2_TAG = "dagda_s2_search_and_destroy"
_S2_DURATION = 15.0


def make_dagda(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Dagda"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Counter Technique", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_DEFENSIVE,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Search and Destroy", slot="S2", sp_cost=34, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
