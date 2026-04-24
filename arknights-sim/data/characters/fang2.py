"""Fang the Wanderer (历阵锐枪芬) — 5★ Pioneer Vanguard alter.

S1 "Spear Throw": sp_cost=30, initial_sp=15, duration=10s, AUTO_TIME, MANUAL
  (DP recovery + attack range extends; range expansion not modeled — stub).
S2 "Vanguard's Valor": sp_cost=45, initial_sp=25, duration=15s, AUTO_TIME, MANUAL
  (ATK+X% + DP generation; DP economy not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.fang2 import make_fang2 as _base_stats

PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "fang2_s1_spear_throw"
_S1_DURATION = 10.0

_S2_TAG = "fang2_s2_vanguards_valor"
_S2_DURATION = 15.0


def make_fang2(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Fang the Wanderer"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = PIONEER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Spear Throw", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Vanguard's Valor", slot="S2", sp_cost=45, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
