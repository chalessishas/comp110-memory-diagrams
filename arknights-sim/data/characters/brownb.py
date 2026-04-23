"""Beehunter (猎蜂) — 4★ Fighter Guard.

S1 "High Mobility": passive 40% physical dodge (always active; no SkillComponent — stub).
S2 "Soaring Fists": sp_cost=30, initial_sp=0, duration=10s, AUTO_TIME, MANUAL
  (attack interval −55% for 10s; ATK_INTERVAL ratio reduction — no sim precedent for RATIO stack — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.brownb import make_brownb as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S2_TAG = "brownb_s2_soaring_fists"
_S2_DURATION = 10.0


def make_brownb(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Beehunter"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S2":
        op.skill = SkillComponent(
            name="Soaring Fists", slot="S2", sp_cost=30, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
