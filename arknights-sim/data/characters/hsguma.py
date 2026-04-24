"""Panda (星熊 / Hoshiguma) — 6★ Defender (Protector) (char_136).

S1 "Warpath": sp_cost=40, initial_sp=20, duration=30s, AUTO_TIME, MANUAL.
  ATK+40%, DEF+80%.

S2 "Thorns": passive (sp_type=NONE), DEF+30% counter-attack — stub.

S3 "Saw of Strength": sp_cost=50, initial_sp=30, duration=25s, MANUAL, AUTO_TIME.
  ATK+140%, DEF+90%; multi-tile AoE not modeled — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.hsguma import make_hsguma as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "hsguma_s1_warpath"
_S1_ATK_RATIO = 0.40
_S1_DEF_RATIO = 0.80
_S1_ATK_BUFF_TAG = "hsguma_s1_atk"
_S1_DEF_BUFF_TAG = "hsguma_s1_def"
_S1_DURATION = 30.0

_S2_TAG = "hsguma_s2_thorns"
_S2_DURATION = 0.0

_S3_TAG = "hsguma_s3_saw"
_S3_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_DEF_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_hsguma(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Hoshiguma"
    op.archetype = RoleArchetype.DEF_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Warpath", slot="S1", sp_cost=40, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Thorns", slot="S2", sp_cost=0, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Saw of Strength", slot="S3", sp_cost=50, initial_sp=30,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
