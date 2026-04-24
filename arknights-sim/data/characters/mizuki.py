"""Mizuki (水月) — 6★ Specialist (Pusher).

S1: sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=40, initial_sp=20, duration=20s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=60, initial_sp=30, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.mizuki import make_mizuki as _base_stats

SPEC_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "mizuki_s1"; _S1_DURATION = 0.0
_S2_TAG = "mizuki_s2"; _S2_DURATION = 20.0
_S3_TAG = "mizuki_s3"; _S3_DURATION = 25.0

def make_mizuki(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Mizuki"
    op.archetype = RoleArchetype.SPEC_PUSHER
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Mizuki S1", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Mizuki S2", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Mizuki S3", slot="S3", sp_cost=60, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
