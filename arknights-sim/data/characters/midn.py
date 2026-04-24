"""Midnight (午夜) — 4★ Guard (Fighter).

S1 "Weapon Enchantment α" (skchr_midn_1): sp_cost=70, initial_sp=30, duration=40s, AUTO_TIME, MANUAL.
  ATK+35%.

char_table confirms only 1 skill slot; stub S2 removed.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.midn import make_midn as _base_stats

GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "midn_s1_weapon_enchant"
_S1_ATK_RATIO = 0.35
_S1_ATK_BUFF_TAG = "midn_s1_atk"
_S1_DURATION = 40.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_ATK_BUFF_TAG))


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_ATK_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_midn(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Midnight"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Weapon Enchantment α", slot="S1", sp_cost=70, initial_sp=30,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
