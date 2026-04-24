"""Iris (爱丽丝) — 6★ Caster (Phalanx) (char_338).

S1: sp_cost=20, initial_sp=10, duration=15s, AUTO_TIME, MANUAL (stub).
S2: sp_cost=50, initial_sp=25, duration=20s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=70, initial_sp=35, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.iris import make_iris as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "iris_s1"; _S1_DURATION = 15.0
_S2_TAG = "iris_s2"; _S2_DURATION = 20.0
_S3_TAG = "iris_s3"; _S3_DURATION = 30.0

def make_iris(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Iris"
    op.archetype = RoleArchetype.CASTER_PHALANX
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Iris S1", slot="S1", sp_cost=20, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Iris S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Iris S3", slot="S3", sp_cost=70, initial_sp=35,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
