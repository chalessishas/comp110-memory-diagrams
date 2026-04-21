"""Specter (幽灵鲨) — 4★ Guard (Fighter).

S1 "ATK Up γ" (shared): sp_cost=30, initial_sp=15, duration=30s, MANUAL, AUTO_TIME.
  ATK +100%.

S2 "Bone Fracture": sp_cost=40, initial_sp=35, duration=15s, MANUAL, AUTO_TIME.
  ATK +160% + STUN 10s on hit (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.ghost import make_ghost as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "ghost_s1_atk_up"
_S1_ATK_RATIO = 1.00
_S1_BUFF_TAG = "ghost_s1_atk"
_S1_DURATION = 30.0
_S2_TAG = "ghost_s2_bone_fracture"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Ghost S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_ghost(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Ghost"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up γ", slot="S1", sp_cost=30, initial_sp=15,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Bone Fracture", slot="S2", sp_cost=40, initial_sp=35,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
