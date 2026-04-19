"""Exusiai — 6* Sniper (Marksman archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 "Only Orange II": +100 ASPD for 30s (sp_cost=5, initial=3) — halves attack interval.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.exusiai import make_exusiai as _base_stats


MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))

_S2_TAG = "exusiai_s2_only_orange"
_S2_ASPD_BONUS = 100.0
_S2_BUFF_TAG = "exusiai_s2_aspd"


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ASPD, stack=BuffStack.FLAT,
        value=_S2_ASPD_BONUS, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_exusiai(slot: str = "S2") -> UnitState:
    """Exusiai E2 max, trust 100. Base stats from akgd; S2 wired."""
    op = _base_stats()
    op.name = "Exusiai"
    op.archetype = RoleArchetype.SNIPER_MARKSMAN
    op.range_shape = MARKSMAN_RANGE
    op.cost = 16
    if slot == "S2":
        op.skill = SkillComponent(
            name="Only Orange",
            slot="S2",
            sp_cost=5,
            initial_sp=3,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
        )
    return op
