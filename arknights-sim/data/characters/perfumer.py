"""Perfumer (调香师) — 5* Medic (Ring-healer archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent "熏衣香" (E2): While deployed, all allies recover HP equal to
  5% of Perfumer's ATK per second (global passive HoT, no range restriction).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import AttackType, Faction, Profession, RoleArchetype
from core.systems.talent_registry import register_talent
from data.characters.generated.flower import make_flower as _base_stats


MEDIC_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 2) for dy in range(-1, 2)
))

_PASSIVE_TAG = "perfumer_passive_hot"
_HEAL_RATE = 0.05   # 5% of ATK per second (E2 talent)
_ACCUM_KEY = "_perfumer_hot_accum"


def _on_tick(world, perfumer: UnitState, dt: float) -> None:
    """Accumulate fractional heal; apply integer HP to all alive deployed allies."""
    accum = getattr(perfumer, _ACCUM_KEY, 0.0) + perfumer.effective_atk * _HEAL_RATE * dt
    whole = int(accum)
    if whole > 0:
        for ally in world.allies():
            if not ally.deployed or ally.hp >= ally.max_hp:
                continue
            healed = ally.heal(whole)
            world.global_state.total_healing_done += healed
    setattr(perfumer, _ACCUM_KEY, accum - whole)


register_talent(_PASSIVE_TAG, on_tick=_on_tick)


def make_perfumer() -> UnitState:
    """Perfumer E2 max, trust 100. Passive HoT: all allies +5% ATK HP/s."""
    op = _base_stats()
    op.name = "Perfumer"
    op.archetype = RoleArchetype.MEDIC_ST
    op.range_shape = MEDIC_RANGE
    op.block = 1
    op.cost = 16
    op.talents = [TalentComponent(
        name="Lavender (passive HoT)",
        behavior_tag=_PASSIVE_TAG,
    )]
    return op
