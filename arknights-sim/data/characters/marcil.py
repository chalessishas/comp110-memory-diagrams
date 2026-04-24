"""Marcille (玛露西尔) — 6★ Caster (Splash).

S1 "A Top Student's Abilities": sp_cost=80, initial_sp=25, duration=9999s (toggle), AUTO_TIME, MANUAL.
  ATK+85%. Toggle off not modeled (treated as permanent buff until skill re-trigger).
S2 "Ancient Magic": sp_cost=80, initial_sp=10, duration=30s, AUTO_TIME, MANUAL (stub).
  AoE Arts burst not modeled.
S3 "Miracle Art": sp_cost=80, initial_sp=40, duration=30s, AUTO_TIME, MANUAL (stub).
  Summon/polymorph not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.marcil import make_marcil as _base_stats

CAST_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "marcil_s1_top_student"
_S1_ATK_RATIO = 0.85
_S1_BUFF_TAG = "marcil_s1_atk"
_S1_DURATION = 9999.0

_S2_TAG = "marcil_s2"
_S2_DURATION = 30.0

_S3_TAG = "marcil_s3"
_S3_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Marcille S1 — ATK+{_S1_ATK_RATIO:.0%} (toggle; deactivation not modeled)")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_marcil(slot: str = "S3") -> UnitState:
    op = _base_stats()
    op.name = "Marcille"
    op.archetype = RoleArchetype.CASTER_SPLASH
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CAST_RANGE
    if slot == "S1":
        op.skill = SkillComponent(name="A Top Student's Abilities", slot="S1", sp_cost=80, initial_sp=25,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG)
    elif slot == "S2":
        op.skill = SkillComponent(name="Ancient Magic", slot="S2", sp_cost=80, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG)
    elif slot == "S3":
        op.skill = SkillComponent(name="Miracle Art", slot="S3", sp_cost=80, initial_sp=40,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG)
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
