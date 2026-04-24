"""Udflow (深巡) — 5★ Defender (Guardian) (char_4137_udflow).

S1 "Incursion Response": sp_cost=30, initial_sp=15, duration=30s, AUTO_TIME, MANUAL.
  ATK+50%, DEF+50%.

S2: sp_cost=45, initial_sp=22, duration=25s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.udflow import make_udflow as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "udflow_s1_incursion"
_S1_ATK_RATIO = 0.50
_S1_DEF_RATIO = 0.50
_S1_ATK_BUFF_TAG = "udflow_s1_atk"
_S1_DEF_BUFF_TAG = "udflow_s1_def"
_S1_DURATION = 30.0

_S2_TAG = "udflow_s2"
_S2_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_DEF_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_udflow(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Udflow"
    op.archetype = RoleArchetype.DEF_GUARDIAN
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Incursion Response", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Udflow S2", slot="S2", sp_cost=45, initial_sp=22,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
