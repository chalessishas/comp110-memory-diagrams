"""Wild Mane (野鬃) — 5★ Vanguard (Charger) (char_496_wildmn).

S1 "骑枪刺击" (Cavalry Thrust): sp_cost=0, initial_sp=0, duration=30s, ON_DEPLOY, AUTO.
  ASPD+135 for 30s from deployment.

S2: sp_cost=25, initial_sp=12, duration=15s — stub.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.wildmn import make_wildmn as _base_stats

OP_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "wildmn_s1_cavalry_thrust"
_S1_ASPD_VALUE = 135.0
_S1_ASPD_BUFF_TAG = "wildmn_s1_aspd"
_S1_DURATION = 30.0

_S2_TAG = "wildmn_s2"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_VALUE, source_tag=_S1_ASPD_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]
    carrier.skill.sp = -1.0  # one-shot: ON_DEPLOY skill fires once per deployment


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_wildmn(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Wild Mane"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = OP_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Cavalry Thrust", slot="S1", sp_cost=0, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.ON_DEPLOY,
            trigger=SkillTrigger.AUTO, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Wild Mane S2", slot="S2", sp_cost=25, initial_sp=12,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
