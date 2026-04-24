"""Bassline (深律) — 5★ Defender (Guardian).

S1 "First Aid": sp_cost=5, initial_sp=0, instant, AUTO_TIME, AUTO
  (next attack heals nearby ally ≤50% HP for 150% ATK; 2 charges — stub).
S2 "Calming Bass": sp_cost=60, initial_sp=50, duration=60s, AUTO_TIME, MANUAL
  (ATK+50%; stops attacking, heals nearby allies; barrier = 50% ATK vs Arts — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.baslin import make_baslin as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "baslin_s1_first_aid"
_S1_DURATION = 0.0

_S2_TAG = "baslin_s2_calming_bass"
_S2_DURATION = 60.0


def make_baslin(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Bassline"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="First Aid", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Calming Bass", slot="S2", sp_cost=60, initial_sp=50,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
