"""Chiave (奇亚韦) — 5★ Vanguard (Pioneer).

S1 "Charge γ": sp_cost=35, initial_sp=20, duration=0s (DP gain, stub).

S2 "Blazing Wire Stripper": sp_cost=45, initial_sp=35, duration=0s
  (DP gain + Arts AoE + RES debuff, stub — requires DP system + AoE dispatch).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.chiave import make_chiave as _base_stats

PIONEER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "chiave_s1_charge"
_S1_DURATION = 0.0

_S2_TAG = "chiave_s2_blazing_wire_stripper"
_S2_DURATION = 0.0


def make_chiave(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Chiave"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = PIONEER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Charge γ", slot="S1", sp_cost=35, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Blazing Wire Stripper", slot="S2", sp_cost=45, initial_sp=35,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
