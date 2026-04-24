"""Specter the Unchained (归溟幽灵鲨) — 6★ Specialist (Dollkeeper) (char_1023_ghost2).

S1 "生存的技巧" (Survival Techniques): sp_cost=35, initial_sp=25, duration=25s, AUTO_TIME, MANUAL.
  ATK+150%.

S2 "生存的渴望" (Survival Desire): sp_cost=35, initial_sp=25, duration=20s, AUTO_TIME, MANUAL.
  ATK+130%, ASPD+50.

S3: sp_cost=50, initial_sp=25, duration=25s — complex mechanic, stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.ghost2 import make_ghost2 as _base_stats

SPEC_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "ghost2_s1_survival_techniques"
_S1_ATK_RATIO = 1.50
_S1_ATK_BUFF_TAG = "ghost2_s1_atk"
_S1_DURATION = 25.0

_S2_TAG = "ghost2_s2_survival_desire"
_S2_ATK_RATIO = 1.30
_S2_ASPD_VALUE = 50.0
_S2_ATK_BUFF_TAG = "ghost2_s2_atk"
_S2_ASPD_BUFF_TAG = "ghost2_s2_aspd"
_S2_DURATION = 20.0

_S3_TAG = "ghost2_s3"
_S3_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ATK_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S2_ASPD_VALUE, source_tag=_S2_ASPD_BUFF_TAG))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_ASPD_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_ghost2(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Specter the Unchained"
    op.archetype = RoleArchetype.SPEC_DOLLKEEPER
    op.profession = Profession.SPECIALIST
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SPEC_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Survival Techniques", slot="S1", sp_cost=35, initial_sp=25,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Survival Desire", slot="S2", sp_cost=35, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Specter the Unchained S3", slot="S3", sp_cost=50, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
