"""Bagpipe (风笛) — 5★ Vanguard (Pioneer).

S1 "Swift Strike γ" (shared skcom_quickattack[3]):
  sp_cost=35, initial_sp=15, duration=35s, MANUAL, AUTO_TIME.
  ATK +45%, ASPD +45.

S2 "High-Impact Assault": sp_cost=4, initial_sp=0, duration=0s (stub).

S3 "Locked Breech Burst": sp_cost=40, initial_sp=25, duration=20s, MANUAL, AUTO_TIME.
  ATK +120%, DEF +120%, block +1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.bpipe import make_bpipe as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "bpipe_s1_swift_strike"
_S1_ATK_RATIO = 0.45
_S1_ASPD_BONUS = 45.0
_S1_ATK_BUFF_TAG = "bpipe_s1_atk"
_S1_ASPD_BUFF_TAG = "bpipe_s1_aspd"
_S1_DURATION = 35.0

_S2_TAG = "bpipe_s2_high_impact"
_S2_DURATION = 0.0

_S3_TAG = "bpipe_s3_locked_breech"
_S3_ATK_RATIO = 1.20
_S3_DEF_RATIO = 1.20
_S3_BLOCK_BONUS = 1
_S3_ATK_BUFF_TAG = "bpipe_s3_atk"
_S3_DEF_BUFF_TAG = "bpipe_s3_def"
_S3_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG))
    world.log(f"Bpipe S1 — ATK+{_S1_ATK_RATIO*100:.0f}% ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_ASPD_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s3_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S3_ATK_RATIO, source_tag=_S3_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S3_DEF_RATIO, source_tag=_S3_DEF_BUFF_TAG))
    carrier.block += _S3_BLOCK_BONUS
    world.log(f"Bpipe S3 — ATK+{_S3_ATK_RATIO*100:.0f}% DEF+{_S3_DEF_RATIO*100:.0f}% block+{_S3_BLOCK_BONUS}/{_S3_DURATION}s")


def _s3_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S3_ATK_BUFF_TAG, _S3_DEF_BUFF_TAG)]
    carrier.block -= _S3_BLOCK_BONUS


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_bpipe(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Bpipe"
    op.archetype = RoleArchetype.VAN_PIONEER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Swift Strike γ", slot="S1", sp_cost=35, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="High-Impact Assault", slot="S2", sp_cost=4, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Locked Breech Burst", slot="S3", sp_cost=40, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
