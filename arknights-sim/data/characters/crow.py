"""La Pluma (羽毛笔) — 4★ Guard (Fighter).

S1 "Rapid Slashing": sp_cost=3, initial_sp=0, instant, AUTO_ATTACK, AUTO
  (next attack hits twice at 135% ATK — double-hit stub).
S2 "Reap": sp_cost=44, initial_sp=30, duration=25s. ATK+55%.
  Interval reduction (×0.65) and conditional vs low-HP not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.crow import make_crow as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "crow_s1_rapid_slashing"
_S1_DURATION = 0.0

_S2_TAG = "crow_s2_reap"
_S2_ATK_RATIO = 0.55
_S2_BUFF_TAG = "crow_s2_atk"
_S2_DURATION = 25.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"La Pluma S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (interval/conditional not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_crow(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "La Pluma"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Rapid Slashing", slot="S1", sp_cost=3, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Reap", slot="S2", sp_cost=44, initial_sp=30,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
