"""Zebra (暴雨) — 6★ Defender (Guardian) (char_304_zebra).

S1 "Emergency Camouflage": sp_cost=4, initial_sp=0, duration=4s, AUTO_TIME, AUTO.
  HP regen — stub.

S2 "Group Camouflage": sp_cost=40, initial_sp=25, duration=20s, AUTO_TIME, MANUAL.
  HP+55%, DEF+55%.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.zebra import make_zebra as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "zebra_s1_emergency_camo"
_S1_DURATION = 4.0

_S2_TAG = "zebra_s2_group_camo"
_S2_HP_RATIO = 0.55
_S2_DEF_RATIO = 0.55
_S2_HP_BUFF_TAG = "zebra_s2_hp"
_S2_DEF_BUFF_TAG = "zebra_s2_def"
_S2_DURATION = 20.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.MAX_HP, stack=BuffStack.RATIO,
                              value=_S2_HP_RATIO, source_tag=_S2_HP_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_HP_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_zebra(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Zebra"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Emergency Camouflage", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Group Camouflage", slot="S2", sp_cost=40, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
