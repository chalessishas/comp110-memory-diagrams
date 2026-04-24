"""Lemuen (char) — 6★ Sniper (Deadeye).

S1: sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2: sp_cost=50, initial_sp=25, duration=25s, AUTO_TIME, MANUAL (stub).
S3: sp_cost=65, initial_sp=32, duration=30s, AUTO_TIME, MANUAL (stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.lemuen import make_lemuen as _base_stats

SNP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 4) for dy in range(-1, 2)))
_S1_TAG = "lemuen_s1"; _S1_DURATION = 0.0
_S2_TAG = "lemuen_s2"; _S2_DURATION = 25.0
_S3_TAG = "lemuen_s3"; _S3_DURATION = 30.0

def make_lemuen(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Lemuen"
    op.archetype = RoleArchetype.SNIPER_DEADEYE
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Lemuen S1", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Lemuen S2", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Lemuen S3", slot="S3", sp_cost=65, initial_sp=32,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
