"""Bibeak (柏喙) — 4★ Swordmaster Guard.

S1 "Plumage Pins": sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack 150% phys + 150% Arts to another target; dual-type split + multi-target — stub).
S2 "Blade Swap": sp_cost=10, initial_sp=2, instant, AUTO_ATTACK, MANUAL
  (170% Arts to ≤6 targets + Stun 1.2s, 3 charges; AoE Arts + stun + charges — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.bibeak import make_bibeak as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "bibeak_s1_plumage_pins"
_S1_DURATION = 0.0

_S2_TAG = "bibeak_s2_blade_swap"
_S2_DURATION = 0.0


def make_bibeak(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Bibeak"
    op.archetype = RoleArchetype.GUARD_SWORDMASTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Plumage Pins", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Blade Swap", slot="S2", sp_cost=10, initial_sp=2,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
