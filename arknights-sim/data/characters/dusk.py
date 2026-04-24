"""Dusk (夕) — 6★ Painter Caster (Supporter subclass).

S1 "Silent Reeds": sp_cost=6, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (range/mode switch between normal and painting targets; range toggle not modeled — stub).
S2 "Under the Ink": sp_cost=40, initial_sp=20, duration=30s, AUTO_TIME, MANUAL
  (summons Inky on field, deals AoE Arts; summon not modeled — stub).
S3 "A Thousand Miles of Rivers and Mountains": sp_cost=80, initial_sp=40, duration=20s, AUTO_TIME, MANUAL
  (full-field landscape summon + AoE Arts on all enemies; complex terrain — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.dusk import make_dusk as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "dusk_s1_silent_reeds"
_S1_DURATION = 0.0

_S2_TAG = "dusk_s2_under_the_ink"
_S2_DURATION = 30.0

_S3_TAG = "dusk_s3_thousand_miles"
_S3_DURATION = 20.0


def make_dusk(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Dusk"
    op.archetype = RoleArchetype.CASTER_PHALANX
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Silent Reeds", slot="S1", sp_cost=6, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Under the Ink", slot="S2", sp_cost=40, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="A Thousand Miles of Rivers and Mountains", slot="S3",
            sp_cost=80, initial_sp=40, duration=_S3_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
