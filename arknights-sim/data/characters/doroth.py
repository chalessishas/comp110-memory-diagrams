"""Dorothy (多萝西) — 5★ Artificer Specialist.

S1 "Mycotoxin Capsule": sp_cost=30, initial_sp=15, instant, AUTO_TIME, MANUAL
  (places fungal device that stuns/slows enemies; device mechanic not modeled — stub).
S2 "Environmental Manipulation": sp_cost=55, initial_sp=25, instant, AUTO_TIME, MANUAL
  (upgrades existing device + AoE stun; chained device system not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.doroth import make_doroth as _base_stats

SPEC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 3) for dy in range(-1, 2)
))

_S1_TAG = "doroth_s1_mycotoxin_capsule"
_S1_DURATION = 0.0

_S2_TAG = "doroth_s2_environmental_manipulation"
_S2_DURATION = 0.0


def make_doroth(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Dorothy"
    op.archetype = RoleArchetype.SPEC_GEEK
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Mycotoxin Capsule", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Environmental Manipulation", slot="S2", sp_cost=55, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
