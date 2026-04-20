"""Lumen (流明) — 6* Medic (Multi-Target archetype).

MEDIC_MULTI trait: heals 3 most-injured allies simultaneously per attack.
  Each hit heals the 3 allies with the lowest hp/max_hp ratio.

S2 "Group Recovery": ATK +30%, heal targets 3 → 5 for 15s.
  sp_cost=20, initial_sp=10, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100, char_4042_lumen).
  HP=1825, ATK=585, DEF=141, RES=10, atk_interval=2.85s, cost=23, block=1.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.lumen import make_lumen as _base_stats


MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(0, 4) for dy in range(-1, 2)
))

_S2_TAG = "lumen_s2_group_recovery"
_S2_ATK_RATIO = 0.30
_S2_BUFF_TAG = "lumen_s2_atk"
_S2_HEAL_TARGETS = 5
_S2_DURATION = 15.0

_BASE_HEAL_TARGETS = 3


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.heal_targets = _S2_HEAL_TARGETS
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.heal_targets = _BASE_HEAL_TARGETS
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_lumen(slot: str = "S2") -> UnitState:
    """Lumen E2 max. MEDIC_MULTI: heals 3 most-injured allies per attack."""
    op = _base_stats()
    op.name = "Lumen"
    op.archetype = RoleArchetype.MEDIC_MULTI
    op.profession = Profession.MEDIC
    op.attack_type = AttackType.HEAL
    op.attack_range_melee = False
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 23
    op.heal_targets = _BASE_HEAL_TARGETS

    if slot == "S2":
        op.skill = SkillComponent(
            name="Group Recovery",
            slot="S2",
            sp_cost=20,
            initial_sp=10,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S2_TAG,
        )
    return op
