"""La Pluma (羽毛笔) — 4★ Guard (Fighter).

S1 "Rapid Slashing": sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack hits twice at 135% ATK — double-hit stub).
S2 "Reap": sp_cost=44, initial_sp=30, duration=25s, AUTO_TIME, MANUAL
  (ATK+55%, interval ×0.65, conditional +40% vs low-HP — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.crow import make_crow as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "crow_s1_rapid_slashing"
_S1_DURATION = 0.0

_S2_TAG = "crow_s2_reap"
_S2_DURATION = 25.0


def make_crow(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "La Pluma"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Rapid Slashing", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Reap", slot="S2", sp_cost=44, initial_sp=30,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
