"""Skyfire (炎熔) — 5★ Caster (Splash).

S1 "ATK Up γ" (shared): sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  ATK +100%.

S2 "Fire of Heaven": sp_cost=25, initial_sp=0, duration=40s, MANUAL, AUTO_TIME.
  base_attack_time+0.7s + ATK×240% AoE + STUN on hit (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.skfire import make_skfire as _base_stats

CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

_S1_TAG = "skfire_s1_atk_up"
_S1_ATK_RATIO = 1.00
_S1_BUFF_TAG = "skfire_s1_atk"
_S1_DURATION = 30.0
_S2_TAG = "skfire_s2_fire_of_heaven"
_S2_DURATION = 40.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Skfire S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_skfire(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Skfire"
    op.archetype = RoleArchetype.CASTER_SPLASH
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Fire of Heaven", slot="S2", sp_cost=25, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
