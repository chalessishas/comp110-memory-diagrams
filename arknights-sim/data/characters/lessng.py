"""Lessing (止颂) — 6★ Guard (Lord).

S1 "Power Strike γ": sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
  Next attack 225% ATK single-hit multiplier.
S2 "Clash of the Faithful": sp_cost=0, initial_sp=0, duration=21s, ON_DEPLOY, AUTO (stub).
  ATK+35%, 2-hit combo attacks. Double-hit not modeled.
S3 "Oathbreaker": sp_cost=45, initial_sp=25, duration=20s, AUTO_TIME, MANUAL (stub).
  MaxHP+80%, attacks deal 180% ATK to blocked targets.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import AttackType, Profession, RoleArchetype, SkillTrigger, SPGainMode
from data.characters.generated.lessng import make_lessng as _base_stats

LORD_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))
_S1_TAG = "lessng_s1"; _S1_DURATION = 0.0
_S2_TAG = "lessng_s2"; _S2_DURATION = 21.0
_S3_TAG = "lessng_s3"; _S3_DURATION = 20.0

def make_lessng(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Lessing"
    op.archetype = RoleArchetype.GUARD_LORD
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = LORD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="Lessing S1", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Clash of the Faithful", slot="S2", sp_cost=0, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Oathbreaker", slot="S3", sp_cost=45, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
