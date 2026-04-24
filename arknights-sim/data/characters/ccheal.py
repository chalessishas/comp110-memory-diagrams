"""Gavial (嘉维尔) — 5★ Medic (ST).

S1 "Vitality Restoration": sp_cost=9, initial_sp=0, duration=4s, AUTO_TIME, AUTO
  (conditional HP-threshold heal + 2 charges — stub).
S2 "Vitality Restoration - Wide Range": sp_cost=60, initial_sp=40, duration=7s, AUTO_TIME, MANUAL
  (AoE heal with conditional scaling — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.ccheal import make_ccheal as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_S1_TAG = "ccheal_s1_vitality_restoration"
_S1_DURATION = 4.0

_S2_TAG = "ccheal_s2_vitality_restoration_wide"
_S2_DURATION = 7.0


def make_ccheal(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Gavial"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Vitality Restoration", slot="S1", sp_cost=9, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Vitality Restoration - Wide Range", slot="S2", sp_cost=60, initial_sp=40,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
