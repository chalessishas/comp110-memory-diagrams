"""Lasher (衡沙) — 4★ Supporter (Decel) (char_4140_lasher).

S1 "Wind Up": sp_cost=30, initial_sp=20, duration=10s, AUTO_TIME, MANUAL.
  ASPD+60.

S2: sp_cost=35, initial_sp=18, duration=20s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.lasher import make_lasher as _base_stats

SUP_RANGE = RangeShape(tiles=tuple((dx, dy) for dx in range(0, 3) for dy in range(-1, 2)))

_S1_TAG = "lasher_s1_wind_up"
_S1_ASPD_VALUE = 60.0
_S1_ASPD_BUFF_TAG = "lasher_s1_aspd"
_S1_DURATION = 10.0

_S2_TAG = "lasher_s2"
_S2_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_lasher(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Lasher"
    op.archetype = RoleArchetype.SUP_DECEL
    op.profession = Profession.SUPPORTER
    op.attack_type = AttackType.ARTS
    op.range_shape = SUP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Wind Up", slot="S1", sp_cost=30, initial_sp=20,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Lasher S2", slot="S2", sp_cost=35, initial_sp=18,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
