"""Swire (史尔特尔) — 5★ Guard (Fighter).

S1 "Objective Completed": sp_cost=5, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
S2 "Cooperative Combat": sp_cost=50, initial_sp=20, duration=21s, AUTO_ATTACK, MANUAL.
  ATK+50%. First talent boost not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.swire import make_swire as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "swire_s1"
_S1_DURATION = 0.0

_S2_TAG = "swire_s2_cooperative_combat"
_S2_ATK_RATIO = 0.50
_S2_BUFF_TAG = "swire_s2_atk"
_S2_DURATION = 21.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Swire S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (talent boost not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_swire(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Swire"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Objective Completed", slot="S1", sp_cost=5, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Cooperative Combat", slot="S2", sp_cost=50, initial_sp=20,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
