"""Greyy (格雷伊) — 4★ Caster (Splash).

S1 "Tactical Chant β" (shared skcom_magic_rage[2]):
  sp_cost=35, initial_sp=10, duration=25s, MANUAL, AUTO_TIME.
  ASPD +75.

S2 "Electrostatic Discharge": sp_cost=60, initial_sp=0, duration=30s, MANUAL, AUTO_TIME.
  ASPD+80 + talent_scale×2 (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.greyy import make_greyy as _base_stats

CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

_S1_TAG = "greyy_s1_tactical_chant"
_S1_ASPD_BONUS = 75.0
_S1_ASPD_BUFF_TAG = "greyy_s1_aspd"
_S1_DURATION = 25.0
_S2_TAG = "greyy_s2_electrostatic"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG))
    world.log(f"Greyy S1 — ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_greyy(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Greyy"
    op.archetype = RoleArchetype.CASTER_SPLASH
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Chant β", slot="S1", sp_cost=35, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Electrostatic Discharge", slot="S2", sp_cost=60, initial_sp=0,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
