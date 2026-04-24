"""Skadi2 (Skadi the Corrupting Heart 海沫) — 6★ Supporter (Hexer).

S1: sp_cost=15, initial_sp=8, duration=5s, AUTO_TIME, AUTO (stub).
S2: sp_cost=30, initial_sp=15, duration=15s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=45, initial_sp=22, duration=25s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.skadi2 import make_skadi2 as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "skadi2_s1"; _S1_DURATION = 5.0
_S2_TAG = "skadi2_s2"; _S2_DURATION = 15.0
_S3_TAG = "skadi2_s3"; _S3_DURATION = 25.0

def make_skadi2(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Skadi the Corrupting Heart"
    op.archetype = RoleArchetype.SUP_HEXER
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Skadi the Corrupting Heart S1", slot="S1", sp_cost=15, initial_sp=8,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Skadi the Corrupting Heart S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Skadi the Corrupting Heart S3", slot="S3", sp_cost=45, initial_sp=22,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
