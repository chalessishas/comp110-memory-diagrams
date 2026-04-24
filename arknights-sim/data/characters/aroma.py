"""Aroma (阿罗玛) — 5★ Caster (Mystic).

S1 "Aroma S1": sp_cost=6, initial_sp=4, duration=10s, AUTO_TIME, MANUAL (stub).
S2 "Caution! Wet Floor!": sp_cost=48, initial_sp=21, duration=23s. ATK+80%.
  Bonus Arts damage to Levitated enemies on landing not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.aroma import make_aroma as _base_stats

CASTER_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S1_TAG = "aroma_s1"
_S1_DURATION = 10.0

_S2_TAG = "aroma_s2_wet_floor"
_S2_ATK_RATIO = 0.80
_S2_BUFF_TAG = "aroma_s2_atk"
_S2_DURATION = 23.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Aroma S2 — ATK+{_S2_ATK_RATIO:.0%}/{_S2_DURATION}s (levitate bonus not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_aroma(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Aroma"
    op.archetype = RoleArchetype.CASTER_MYSTIC
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Aroma S1", slot="S1", sp_cost=6, initial_sp=4,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Caution! Wet Floor!", slot="S2", sp_cost=48, initial_sp=21,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
