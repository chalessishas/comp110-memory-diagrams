"""Ayerscarpe (断崖) — 5★ Instructor Guard.

S1 "Shrapnel Burst": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (150% ATK Arts dmg to 3 targets + 1s Slow; Arts swap + multi-target not modeled — stub).
S2 "Activate Phase Blades": sp_cost=53, initial_sp=21, duration=21s, AUTO_TIME, MANUAL
  (range expand + Arts AoE to adjacent-ally-blocked enemies; complex targeting not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.ayer import make_ayer as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "ayer_s1_shrapnel_burst"
_S1_DURATION = 0.0

_S2_TAG = "ayer_s2_phase_blades"
_S2_DURATION = 21.0


def make_ayer(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Ayerscarpe"
    op.archetype = RoleArchetype.GUARD_INSTRUCTOR
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Shrapnel Burst", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Activate Phase Blades", slot="S2", sp_cost=53, initial_sp=21,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
