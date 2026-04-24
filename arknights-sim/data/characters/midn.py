"""Midnight (午夜) — 4★ Guard (Fighter).

S1: sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=35, initial_sp=18, duration=20s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.midn import make_midn as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "midn_s1"; _S1_DURATION = 0.0
_S2_TAG = "midn_s2"; _S2_DURATION = 20.0

def make_midn(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Midnight"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Midnight S1", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Midnight S2", slot="S2", sp_cost=35, initial_sp=18,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
