"""Warfarin (华法琳) — 5★ Single-Target Medic.

S1 "Emergency Triage": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next heal +19% target max HP when <50% HP, 3 charges; conditional + charge not modeled — stub).
S2 "Unstable Plasma": sp_cost=60, initial_sp=45, duration=15s, AUTO_TIME, MANUAL
  (self+random ally ATK+60% + drain 3% max HP/s; random ally targeting + HP drain — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.bldsk import make_bldsk as _base_stats

MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "bldsk_s1_emergency_triage"
_S1_DURATION = 0.0

_S2_TAG = "bldsk_s2_unstable_plasma"
_S2_DURATION = 15.0


def make_bldsk(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Warfarin"
    op.archetype = RoleArchetype.MEDIC_ST
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.range_shape = MEDIC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Emergency Triage", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Unstable Plasma", slot="S2", sp_cost=60, initial_sp=45,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
