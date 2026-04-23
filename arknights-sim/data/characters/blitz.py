"""Blitz (闪击) — 5★ Sentinel Defender.

S1 "Flash Shield": sp_cost=18, initial_sp=10, duration=3.5s, AUTO_TIME, MANUAL
  (Stun all ahead for 3.5s, max 4 uses/deploy; limited-use stun — stub).
S2 "Shield Bash": sp_cost=40, initial_sp=15, duration=6s, AUTO_TIME, MANUAL
  (170% ATK to all blocked + Stun 6s + ASPD+200 + talent×1.4; multi-target + stun combo — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.blitz import make_blitz as _base_stats

DEFENDER_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "blitz_s1_flash_shield"
_S1_DURATION = 3.5

_S2_TAG = "blitz_s2_shield_bash"
_S2_DURATION = 6.0


def make_blitz(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Blitz"
    op.archetype = RoleArchetype.DEF_SENTINEL
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEFENDER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Flash Shield", slot="S1", sp_cost=18, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Shield Bash", slot="S2", sp_cost=40, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
