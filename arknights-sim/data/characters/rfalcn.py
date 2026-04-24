"""Rfalcn (Roberta Falcon 铸铁) — 4★ Vanguard (Pioneer).

S1: sp_cost=0, initial_sp=0, duration=0s, ON_DEPLOY, AUTO (deploy-trigger, stub).
S2: sp_cost=25, initial_sp=12, duration=15s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.rfalcn import make_rfalcn as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "rfalcn_s1"; _S1_DURATION = 0.0
_S2_TAG = "rfalcn_s2"; _S2_DURATION = 15.0

def make_rfalcn(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Roberta Falcon"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Roberta Falcon S1", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Roberta Falcon S2", slot="S2", sp_cost=25, initial_sp=12,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
