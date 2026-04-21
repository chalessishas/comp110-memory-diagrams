"""Estelle (艾丝黛尔) — 4★ Guard (Fighter).

S1 "ATK Up β" (shared): sp_cost=35, initial_sp=10, duration=25s, MANUAL, AUTO_TIME.
  ATK +80%.

S2 "Sacrificial Strike": sp_cost=20, initial_sp=10, duration=15s, MANUAL, AUTO_DEFENSIVE.
  ATK +150% + block set to 0 (complex — not modeled).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.estell import make_estell as _base_stats

MELEE_RANGE = RangeShape(tiles=((0, 0),))

_S1_TAG = "estell_s1_atk_up"
_S1_ATK_RATIO = 0.80
_S1_BUFF_TAG = "estell_s1_atk"
_S1_DURATION = 25.0
_S2_TAG = "estell_s2_sacrifice"
_S2_DURATION = 15.0


def _s1_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(axis=BuffAxis.ATK, stack=BuffStack.RATIO,
                              value=_S1_ATK_RATIO, source_tag=_S1_BUFF_TAG))
    world.log(f"Estell S1 — ATK+{_S1_ATK_RATIO:.0%}/{_S1_DURATION}s")


def _s1_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S1_BUFF_TAG]


register_skill(_S1_TAG, on_start=_s1_on_start, on_end=_s1_on_end)


def make_estell(slot: str = "S1") -> UnitState:
    op = _base_stats()
    op.name = "Estell"
    op.archetype = RoleArchetype.GUARD_FIGHTER
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = MELEE_RANGE
    if slot == "S1":
        op.skill = SkillComponent(
            name="ATK Up β", slot="S1", sp_cost=35, initial_sp=10,
            duration=_S1_DURATION, sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S1_TAG,
        )
    elif slot == "S2":
        op.skill = SkillComponent(
            name="Sacrificial Strike", slot="S2", sp_cost=20, initial_sp=10,
            duration=_S2_DURATION, sp_gain_mode=SPGainMode.AUTO_DEFENSIVE,
            trigger=SkillTrigger.MANUAL, requires_target=False, behavior_tag=_S2_TAG,
        )
    if op.skill:
        op.skill.sp = float(op.skill.initial_sp)
    return op
