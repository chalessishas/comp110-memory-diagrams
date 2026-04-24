"""Magellan (麦哲伦) — 5★ Supporter (Bard).

S1: sp_cost=30, initial_sp=20, duration=15s, AUTO_TIME, MANUAL — stub (freeze/slow complex).

S2 "Laser Mining Module" (skchr_mgllan_2): sp_cost=38, initial_sp=25, duration=15s, AUTO_TIME, MANUAL.
  ASPD+150.

S3 "Armed Combat Module" (skchr_mgllan_3): sp_cost=38, initial_sp=25, duration=15s, AUTO_TIME, MANUAL.
  ATK+150%.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.mgllan import make_mgllan as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "mgllan_s1"
_S1_DURATION = 15.0

_S2_TAG = "mgllan_s2_laser_mining"
_S2_ASPD_VALUE = 150.0
_S2_ASPD_BUFF_TAG = "mgllan_s2_aspd"
_S2_DURATION = 15.0

_S3_TAG = "mgllan_s3_armed_combat"
_S3_ATK_RATIO = 1.50
_S3_ATK_BUFF_TAG = "mgllan_s3_atk"
_S3_DURATION = 15.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S2_ASPD_VALUE, source_tag=_S2_ASPD_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_ASPD_BUFF_TAG]


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG))


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S3_ATK_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)
register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_mgllan(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Magellan"
    op.archetype = RoleArchetype.SUP_BARD
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Magellan S1", slot="S1", sp_cost=30, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Laser Mining Module", slot="S2", sp_cost=38, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Armed Combat Module", slot="S3", sp_cost=38, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
