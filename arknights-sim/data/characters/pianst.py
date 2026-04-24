"""Czerny (车尔尼) — 5★ Defender (Arts Protector) (char_4047_pianst).

S1 "Flying Fingers": sp_cost=35, initial_sp=20, duration=35s, AUTO_TIME, MANUAL.
  ATK+80%, RES+100%.

S2 "Thunderous Performance": sp_cost=30, initial_sp=10, duration=20s, AUTO_TIME, MANUAL.
  HP+100%, stacking ATK on hit — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.pianst import make_pianst as _base_stats

DEF_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "pianst_s1_flying_fingers"
_S1_ATK_RATIO = 0.80
_S1_RES_RATIO = 1.0
_S1_ATK_BUFF_TAG = "pianst_s1_atk"
_S1_RES_BUFF_TAG = "pianst_s1_res"
_S1_DURATION = 35.0

_S2_TAG = "pianst_s2_thunderous"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.RES, stack=BuffStack.RATIO,
                              value=_S1_RES_RATIO, source_tag=_S1_RES_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_RES_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_pianst(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Czerny"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.ARTS
    op.range_shape = DEF_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Flying Fingers", slot="S1", sp_cost=35, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Thunderous Performance", slot="S2", sp_cost=30, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
