"""Siege2 (Siege alter 能天使) — 6★ Guard (Fighter).

S1: sp_cost=5, initial_sp=0, duration=0s, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=45, initial_sp=22, duration=20s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=60, initial_sp=30, duration=25s, AUTO_TIME, MANUAL (stub).
Note: hp=2895, attack_type=ARTS; 6★ Siege alter.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.siege2 import make_siege2 as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))
_S1_TAG = "siege2_s1"; _S1_DURATION = 0.0
_S2_TAG = "siege2_s2"; _S2_DURATION = 20.0
_S3_TAG = "siege2_s3"; _S3_DURATION = 25.0

def make_siege2(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Siege"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.ARTS
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Siege S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Siege S2", slot="S2", sp_cost=45, initial_sp=22,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Siege S3", slot="S3", sp_cost=60, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
