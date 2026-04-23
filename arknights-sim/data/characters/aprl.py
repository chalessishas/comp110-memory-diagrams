"""April (四月) — 4★ Ambusher Sniper.

S1 "Precise Shooting": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack → 200% ATK; single-hit power-shot not modeled — stub).
S2 "Flexible Camouflage": sp_cost=0, initial_sp=0, duration=20s, ON_DEPLOY, AUTO
  (on-deploy ATK+70% + Camouflage; passive deploy-trigger + status not modeled — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, RangeShape
from core.types import (
    AttackType, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from data.characters.generated.aprl import make_aprl as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (2, -1),
    (1, 1), (2, 1),
))

_S1_TAG = "aprl_s1_precise_shooting"
_S1_DURATION = 0.0

_S2_TAG = "aprl_s2_flexible_camouflage"
_S2_DURATION = 20.0


def make_aprl(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "April"
    op.archetype = RoleArchetype.SNIPER_AMBUSHER
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Precise Shooting", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Flexible Camouflage", slot="S2", sp_cost=0, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
