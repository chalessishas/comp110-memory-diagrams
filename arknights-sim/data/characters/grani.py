"""Grani (格拉尼) — 5★ Vanguard (Charger).

S1 "DEF Up γ": sp_cost=40, initial_sp=10, duration=40s, AUTO_TIME, MANUAL.
  DEF+60%.
S2 "Press the Attack!": sp_cost=74, initial_sp=50, duration=30s, AUTO_TIME, MANUAL.
  ATK+60%, DEF+60%, Block+1. "Attacks all blocked simultaneously" not modeled.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.grani import make_grani as _base_stats

VAN_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_S1_TAG = "grani_s1_def_up"
_S1_DEF_RATIO = 0.60
_S1_BUFF_TAG = "grani_s1_def"
_S1_DURATION = 40.0

_S2_TAG = "grani_s2_press_the_attack"
_S2_ATK_RATIO = 0.60
_S2_DEF_RATIO = 0.60
_S2_ATK_BUFF_TAG = "grani_s2_atk"
_S2_DEF_BUFF_TAG = "grani_s2_def"
_S2_DURATION = 30.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S1_DEF_RATIO, source_tag=_S1_BUFF_TAG,
    ))
    world.log(f"Grani S1 — DEF+{_S1_DEF_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_ATK_BUFF_TAG,
    ))
    carrier.buffs.append(Buff(
        axis=BuffAxis.DEF, stack=BuffStack.RATIO,
        value=_S2_DEF_RATIO, source_tag=_S2_DEF_BUFF_TAG,
    ))
    world.log(f"Grani S2 — ATK+{_S2_ATK_RATIO:.0%} DEF+{_S2_DEF_RATIO:.0%}/{_S2_DURATION}s (multi-target not modeled)")


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs
                     if b.source_tag not in (_S2_ATK_BUFF_TAG, _S2_DEF_BUFF_TAG)]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_grani(slot: str = "S2") -> UnitState:
    op = _base_stats()
    op.name = "Grani"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.profession = Profession.VANGUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = VAN_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="DEF Up γ", slot="S1", sp_cost=40, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Press the Attack!", slot="S2", sp_cost=74, initial_sp=50,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
