"""Slent2 (淬羽赫默 / Silence the Paradigmatic) — 6★ Supporter (char_1031_slent2).

S1 "Pioneering Spirit": sp_cost=30, initial_sp=15, duration=25s, AUTO_TIME, MANUAL.
  ATK+80%.

S2: sp_cost=30, initial_sp=15, duration=10s — stub.
S3: sp_cost=50, initial_sp=25, duration=30s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.slent2 import make_slent2 as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "slent2_s1_pioneering"
_S1_ATK_RATIO = 0.80
_S1_ATK_BUFF_TAG = "slent2_s1_atk"
_S1_DURATION = 25.0

_S2_TAG = "slent2_s2"
_S2_DURATION = 10.0

_S3_TAG = "slent2_s3"
_S3_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ATK_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_slent2(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Silence the Paradigmatic"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Pioneering Spirit", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Silence the Paradigmatic S2", slot="S2", sp_cost=30, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    elif slot == "S3":
        op.skill = SkillComponent(
            name="Silence the Paradigmatic S3", slot="S3", sp_cost=50, initial_sp=25,
            duration=_S3_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S3_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
