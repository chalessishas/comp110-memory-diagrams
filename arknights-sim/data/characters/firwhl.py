"""Firewhistle (火哨) — 5★ Defender (Fortress).

S1 "Wildfire": sp_cost=8, initial_sp=0, instant, AUTO_DEFENSIVE, AUTO (stub).
  Charge-based attack buff; exact effect not modeled.
S2 "Scorched Earth": sp_cost=43, initial_sp=19, duration=17s, AUTO_TIME, MANUAL (stub).
  AoE fire field not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.firwhl import make_firwhl as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "firwhl_s1"
_S1_DURATION = 0.0

_S2_TAG = "firwhl_s2"
_S2_DURATION = 17.0


def make_firwhl(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Firewhistle"
    op.archetype = RoleArchetype.DEF_FORTRESS
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Wildfire", slot="S1", sp_cost=8, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_DEFENSIVE,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Scorched Earth", slot="S2", sp_cost=43, initial_sp=19,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
