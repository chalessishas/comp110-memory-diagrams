"""Mousse (慕斯) — 4★ Guard (Fighter, Arts attacker).

S1 "Scratch": sp_cost=4, initial_sp=0, instant, MANUAL, AUTO_ATTACK.
  ATK+75% on next hit + ATK debuff (complex — not modeled).

S2 "Fury": sp_cost=80, initial_sp=45, duration=40s, MANUAL, AUTO_TIME.
  ATK +75%, DEF +75%.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.frncat import make_frncat as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "frncat_s1_scratch"
_S1_DURATION = 0.0
_S2_TAG = "frncat_s2_fury"
_S2_ATK_RATIO = 0.75
_S2_DEF_RATIO = 0.75
_S2_ATK_BUFF_TAG = "frncat_s2_atk"
_S2_DEF_BUFF_TAG = "frncat_s2_def"
_S2_DURATION = 40.0


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG))
    carrier.buffs.append(Buff(axis=BuffAxis.DEF, stack=BuffStack.RATIO,
                              value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG))
    world.log(f"Frncat S2 — ATK+{_S2_ATK_RATIO:.0%} DEF+{_S2_DEF_RATIO:.0%}/{_S2_DURATION}s")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_frncat(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Frncat"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.ARTS
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="Scratch", slot="S1", sp_cost=4, initial_sp=0,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_ATTACK,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Fury", slot="S2", sp_cost=80, initial_sp=45,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
