"""Lava (拉瓦) — 3★ Caster (Core).

S1 "Tactical Chant α" (shared skcom_magic_rage[1]):
  sp_cost=40, initial_sp=0, duration=20s, MANUAL, AUTO_TIME.
  ASPD +50.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.lava import make_lava as _base_stats

CASTER_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
    (1, -1), (1, 1), (2, -1), (2, 1),
))

_S1_TAG = "lava_s1_tactical_chant"
_S1_ASPD_BONUS = 50.0
_S1_ASPD_BUFF_TAG = "lava_s1_aspd"
_S1_DURATION = 20.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
                              value=_S1_ASPD_BONUS, source_tag=_S1_ASPD_BUFF_TAG))
    world.log(f"Lava S1 — ASPD+{_S1_ASPD_BONUS:.0f}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ASPD_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_lava(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Lava"
    op.archetype = RoleArchetype.CASTER_CORE
    op.profession = Profession.CASTER
    op.attack_type = AttackType.ARTS
    op.range_shape = CASTER_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Tactical Chant α", slot="S1", sp_cost=40, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
