"""Thorns (棘刺) — 6* Guard (Standard archetype).

Talent "Thorn Prick": When Thorns receives damage, deals 180% ATK as Arts counter-damage
  to the attacker.

S3 "Annihilation": For 30s, attacks change to AOE mode — simultaneously hitting all
  enemies in range each attack cycle (physical, normal ATK value).
  sp_cost=40, initial_sp=20, AUTO_TIME, AUTO trigger.

Base stats from ArknightsGameData (E2 max, trust 100).
"""
from __future__ import annotations
from math import floor
from core.state.unit_state import UnitState, SkillComponent, RangeShape, TalentComponent
from core.types import (
    AttackType, Faction, Profession,
    RoleArchetype, SkillTrigger, SPGainMode,
)
from core.systems.skill_system import register_skill
from core.systems.talent_registry import register_talent
from data.characters.generated.thorns import make_thorns as _base_stats


GUARD_RANGE = RangeShape(tiles=(
    (0, 0), (1, 0), (2, 0),
    (0, -1), (0, 1),
))

_TALENT_TAG = "thorns_thorn_prick"
_S3_TAG = "thorns_s3_annihilation"
_COUNTER_RATE = 1.80   # 180% ATK arts counter per hit received


# --- Talent: Thorn Prick ---

def _talent_on_hit_received(world, defender: UnitState, attacker: UnitState, damage: int) -> None:
    if damage <= 0 or not attacker.alive:
        return
    counter = int(floor(defender.effective_atk * _COUNTER_RATE))
    dealt = attacker.take_arts(counter)
    if dealt > 0:
        world.global_state.total_damage_dealt += dealt
        world.log(f"Thorns Thorn Prick → {attacker.name}  counter={dealt}  ({attacker.hp}/{attacker.max_hp})")


register_talent(_TALENT_TAG, on_hit_received=_talent_on_hit_received)


# --- S3: Annihilation ---

def _s3_on_start(world, carrier: UnitState) -> None:
    setattr(carrier, "_attack_all_in_range", True)


def _s3_on_end(world, carrier: UnitState) -> None:
    setattr(carrier, "_attack_all_in_range", False)


register_skill(_S3_TAG, on_start=_s3_on_start, on_end=_s3_on_end)


def make_thorns(slot: str = "S3") -> UnitState:
    """Thorns E2 max. Talent: arts counter on hit. S3: AOE attack mode for 30s."""
    op = _base_stats()
    op.name = "Thorns"
    op.archetype = RoleArchetype.GUARD_LORD
    op.profession = Profession.GUARD
    op.range_shape = GUARD_RANGE
    op.cost = 20

    op.talents = [TalentComponent(name="Thorn Prick", behavior_tag=_TALENT_TAG)]

    if slot == "S3":
        op.skill = SkillComponent(
            name="Annihilation",
            slot="S3",
            sp_cost=40,
            initial_sp=20,
            duration=30.0,
            sp_gain_mode=SPGainMode.AUTO_TIME,
            trigger=SkillTrigger.AUTO,
            requires_target=False,
            behavior_tag=_S3_TAG,
        )
    return op
