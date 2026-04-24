"""Kirin R Yato (麒麟R夜刀) — 5★ Specialist (Executor) (char_1029_yato2).

S1 "鬼人化" (Demon Form): sp_cost=0, initial_sp=0, duration=20s, ON_DEPLOY, AUTO.
  ASPD+100 for 20s from deployment.

S2: sp_cost=35, initial_sp=18, duration=20s — stub.
S3: sp_cost=50, initial_sp=25, duration=25s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.yato2 import make_yato2 as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "yato2_s1_demon_form"
_S1_ASPD_VALUE = 100.0
_S1_ASPD_BUFF_TAG = "yato2_s1_aspd"
_S1_DURATION = 20.0

_S2_TAG = "yato2_s2"
_S2_DURATION = 20.0

_S3_TAG = "yato2_s3"
_S3_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]
    carrier.skill.sp = -1.0  # one-shot: ON_DEPLOY skill fires once per deployment


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_yato2(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Kirin R Yato"
    op.archetype = RoleArchetype.SPEC_EXECUTOR
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Demon Form", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Kirin R Yato S2", slot="S2", sp_cost=35, initial_sp=18,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Kirin R Yato S3", slot="S3", sp_cost=50, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
