"""Brigid (水灯心) — 5★ Sniper (Marksman).

S1 "Familiarity": sp_cost=2, initial_sp=0, duration=0s (instant multi-hit, stub).

S2 "Bring to Heel": sp_cost=25, initial_sp=15, duration=25s, MANUAL, AUTO_TIME.
  ATK +50% (sluggish/interval effects not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.brigid import make_brigid as _base_stats

SNIPER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, -1), (2, -1), (3, -1),
    (1, 1), (2, 1), (3, 1),
))

_S1_TAG = "brigid_s1_familiarity"
_S1_DURATION = 0.0

_S2_TAG = "brigid_s2_bring_to_heel"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "brigid_s2_atk"
_S2_DURATION = 25.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG))
    world.log(f"Brigid S2 — ATK+{_S2_ATK_RATIO*100:.0f}%/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_brigid(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Brigid"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.profession = Profession.SNIPER
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = SNIPER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Familiarity", slot="S1", sp_cost=2, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Bring to Heel", slot="S2", sp_cost=25, initial_sp=15,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
