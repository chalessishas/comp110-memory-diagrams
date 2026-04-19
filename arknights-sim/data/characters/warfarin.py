"""Warfarin — 5* Medic (Single-target archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
S2 Sanguinelant: +35% ATK to all deployed allies for 10s (sp_cost=3, fires unconditionally).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from data.characters.generated.warfarin import make_warfarin as _base_stats


MEDIC_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0),
))

_S2_TAG = "warfarin_s2_sanguinelant"
_S2_ATK_RATIO = 0.35
_S2_BUFF_TAG = "warfarin_s2_atk"


def _s2_on_start(world, carrier: UnitState) -> None:
    for ally in world.allies():
        if not ally.alive or not ally.deployed:
            continue
        ally.buffs.append(Buff(
            axis=BuffAxis.ATK, stack=BuffStack.RATIO,
            value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
        ))


def _s2_on_end(world, carrier: UnitState) -> None:
    for ally in world.allies():
        ally.buffs = [b for b in ally.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_warfarin(slot: str = "S2") -> UnitState:
    """Warfarin E2 max, trust 100. S2 Sanguinelant team ATK buff wired."""
    op = _base_stats()
    op.name = "Warfarin"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.attack_type = AttackType.HEAL
    op.cost = 12
    if slot == "S2":
        op.skill = SkillComponent(
            name="Sanguinelant",
            slot="S2",
            sp_cost=3,
            initial_sp=1,
            duration=10.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            behavior_tag=_S2_TAG,
            requires_target=False,   # fires unconditionally — no heal target needed
        )
    return op
