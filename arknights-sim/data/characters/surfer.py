"""Surfer (Surfer) — stub operator.

S1: sp_cost=0, initial_sp=0, duration=0.0s, ON_DEPLOY, AUTO (stub).
S2: sp_cost=25, initial_sp=12, duration=15.0s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.surfer import make_surfer as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "surfer_s1"; _S1_DURATION = 0.0
_S2_TAG = "surfer_s2"; _S2_DURATION = 15.0

def make_surfer(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Surfer"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Surfer S1", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Surfer S2", slot="S2", sp_cost=25, initial_sp=12,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
