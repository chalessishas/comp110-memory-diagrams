"""Czerny (魔王) — Defender (ArtsProtector).

S1 "Fingerfertigkeit": sp_cost=42, initial_sp=12, duration=29s, AUTO_TIME, MANUAL.
  ATK+50% + RES+80 flat.
S2: sp_cost=45, initial_sp=25, duration=20s (conditional ATK stacking + AoE burst — stub).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.cetsyr import make_cetsyr as _base_stats

DEFENDER_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "cetsyr_s1_fingerfertigkeit"
_S1_ATK_RATIO = 0.50
_S1_RES_FLAT = 80.0
_S1_ATK_BUFF_TAG = "cetsyr_s1_atk"
_S1_RES_BUFF_TAG = "cetsyr_s1_res"
_S1_DURATION = 29.0

_S2_TAG = "cetsyr_s2"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.RES, stack=BuffStack.FLAT,
                              value=_S1_RES_FLAT, source_tag=_S1_RES_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ATK_BUFF_TAG, _S1_RES_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_cetsyr(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Czerny"
    op.archetype = RoleArchetype.DEF_ARTS_PROTECTOR
    op.profession = Profession.DEFENDER
    op.attack_type = AttackType.ARTS
    op.range_shape = DEFENDER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Fingerfertigkeit", slot="S1", sp_cost=42, initial_sp=12,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Cetsyr S2", slot="S2", sp_cost=45, initial_sp=25,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
