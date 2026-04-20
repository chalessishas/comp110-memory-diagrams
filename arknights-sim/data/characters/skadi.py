"""Skadi (斯卡蒂) — 6* Guard (Dreadnought archetype).

Talent "Predator": When Skadi kills an enemy, she recovers 15% of max HP.
  Fires via on_kill hook; heals even when at full HP would be a no-op.

S2 "Surge": 30s duration, ATK +130%.
  sp_cost=40, initial_sp=15, AUTO_TIME, AUTO trigger, requires_target=True.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, SkillComponent, Buff, RangeShape, TalentComponent
from core.types import (
    AttackType, BuffAxis, BuffStack, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.skadi import make_skadi as _base_stats


GUARD_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

# --- Talent: Predator ---
_TALENT_TAG = "skadi_predator"
_TALENT_HEAL_RATIO = 0.15    # recover 15% max HP on kill

_S2_TAG = "skadi_s2_surge"
_S2_ATK_RATIO = 1.30         # +130% ATK
_S2_BUFF_TAG = "skadi_s2_atk_buff"
_S2_DURATION = 30.0


def _talent_on_kill(world, killer: UnitState, killed) -> None:
    heal = int(killer.max_hp * _TALENT_HEAL_RATIO)
    healed = killer.heal(heal)
    if healed > 0:
        world.log(f"Skadi Predator kill-heal  +{healed}  ({killer.hp}/{killer.max_hp})")


register_talent(_TALENT_TAG, on_kill=_talent_on_kill)


def _s2_on_start(world, carrier: UnitState) -> None:
    carrier.buffs.append(Buff(
        axis=BuffAxis.ATK, stack=BuffStack.RATIO,
        value=_S2_ATK_RATIO, source_tag=_S2_BUFF_TAG,
    ))


def _s2_on_end(world, carrier: UnitState) -> None:
    carrier.buffs = [b for b in carrier.buffs if b.source_tag != _S2_BUFF_TAG]


register_skill(_S2_TAG, on_start=_s2_on_start, on_end=_s2_on_end)


def make_skadi(slot: str = "S2") -> UnitState:
    """Skadi E2 max. Talent: heal on kill. S2: ATK burst."""
    op = _base_stats()
    op.name = "Skadi"
    op.archetype = RoleArchetype.GUARD_DREADNOUGHT
    op.profession = Profession.GUARD
    op.attack_type = AttackType.PHYSICAL
    op.range_shape = GUARD_RANGE
    op.cost = 19

    op.talents = [TalentComponent(name="Predator", behavior_tag=_TALENT_TAG)]

    if slot == "S2":
        op.skill = SkillComponent(
            name="Surge",
            slot="S2",
            sp_cost=40,
            initial_sp=15,
            duration=_S2_DURATION,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=True,
            behavior_tag=_S2_TAG,
        )
    return op
