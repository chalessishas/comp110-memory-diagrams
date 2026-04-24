"""Flamebringer (炎客) — 5★ Guard (Dreadnought).

S1 "Blood Pact": sp_cost=4, initial_sp=0, instant, AUTO_ATTACK, AUTO (stub).
  Next attack 190% ATK, recovers 6% HP. Per-attack mechanic not modeled.
S2 "Blade Demon": sp_cost=48, initial_sp=0, duration=∞, AUTO_TIME, MANUAL.
  ATK+40%, ASPD+30 (ASPD not modeled). Infinite duration → 9999s.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.flameb import make_flameb as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "flameb_s1"
_S1_DURATION = 0.0

_S2_TAG = "flameb_s2_blade_demon"
_S2_ATK_RATIO = 0.40
_S2_BUFF_TAG = "flameb_s2_atk"
_S2_DURATION = 9999.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))
    world.log(f"Flamebringer S2 — ATK+{_S2_ATK_RATIO:.0%} (ASPD+30 not modeled, infinite duration)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_flameb(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Flamebringer"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Blood Pact", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.AUTO, requires_target=True, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Blade Demon", slot="S2", sp_cost=48, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
