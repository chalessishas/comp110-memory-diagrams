"""Angelina (安洁莉娜) — 6★ Decel Supporter.

S1 "Binding Frost": sp_cost=8, initial_sp=5, instant, AUTO_TIME, AUTO
  (AoE slow + Bind; area slow + status not modeled — stub).
S2 "Frozen Heart": sp_cost=50, initial_sp=25, duration=30s, AUTO_TIME, MANUAL
  (range heal + slow + Bind ring; multi-target complex — stub).
S3 "Blizzard": sp_cost=90, initial_sp=45, duration=20s, AUTO_TIME, MANUAL
  (AoE Freeze, repeated procs; Freeze status + summon not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.aglina import make_aglina as _base_stats

SUPPORTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 4) for dy in range(-2, 3)
))

_S1_TAG = "aglina_s1_binding_frost"
_S1_DURATION = 0.0

_S2_TAG = "aglina_s2_frozen_heart"
_S2_DURATION = 30.0

_S3_TAG = "aglina_s3_blizzard"
_S3_DURATION = 20.0


def make_aglina(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Angelina"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUPPORTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Binding Frost", slot="S1", sp_cost=8, initial_sp=5,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Frozen Heart", slot="S2", sp_cost=50, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Blizzard", slot="S3", sp_cost=90, initial_sp=45,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
