"""Wscoot (骋风) — 6★ Guard (Dreadnought) (char_445_wscoot).

S1 "Defend by Offense": sp_cost=18, initial_sp=10, duration=15s, AUTO_ATTACK, AUTO.
  ASPD+50, DEF+55%.

S2 "Precision Volley": sp_cost=40, initial_sp=15, duration=25s, AUTO_TIME, MANUAL.
  Multi-hit AoE — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.wscoot import make_wscoot as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "wscoot_s1_defend_offense"
_S1_ASPD_VALUE = 50.0
_S1_DEF_RATIO = 0.55
_S1_ASPD_BUFF_TAG = "wscoot_s1_aspd"
_S1_DEF_BUFF_TAG = "wscoot_s1_def"
_S1_DURATION = 15.0

_S2_TAG = "wscoot_s2_precision"
_S2_DURATION = 25.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S1_DEF_RATIO, source_tag=_S1_DEF_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S1_ASPD_BUFF_TAG, _S1_DEF_BUFF_TAG)]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_wscoot(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Wscoot"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Defend by Offense", slot="S1", sp_cost=18, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Precision Volley", slot="S2", sp_cost=40, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
