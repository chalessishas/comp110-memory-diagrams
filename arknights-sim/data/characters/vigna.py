"""Vigna — 4* Vanguard (Charger archetype).

Charger class trait: gains 1 DP when this unit kills an enemy.
Talent "Fierce Stabbing" (E2): 10% crit (×1.5 dmg); 30% during skill active.
  Implemented via crit_chance field on UnitState + world.rng in combat_system.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import AttackType, Faction, Profession, RoleArchetype
from core.systems.talent_registry import register_talent
from data.characters.generated.vigna import make_vigna as _base_stats
from data.characters.registry import _CHARGER_DP_TAG


CHARGER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))

_FIERCE_STABBING_TAG = "vigna_fierce_stabbing"
_CRIT_BASE = 0.10   # 10% when skill inactive
_CRIT_SKILL = 0.30  # 30% when skill active


def _fierce_stabbing_on_tick(world, carrier: UnitState, dt: float) -> None:
    sk = carrier.skill
    is_skill_active = sk is not None and sk.active_remaining > 0
    carrier.crit_chance = _CRIT_SKILL if is_skill_active else _CRIT_BASE


register_talent(_FIERCE_STABBING_TAG, on_tick=_fierce_stabbing_on_tick)


def make_vigna() -> UnitState:
    """Vigna E2 max. Charger trait: +1 DP on kill. Fierce Stabbing: 10%/30% crit."""
    op = _base_stats()
    op.name = "Vigna"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.range_shape = CHARGER_RANGE
    op.block = 1
    op.cost = 11
    op.talents = [
        TalentComponent(name="Fierce Stabbing", behavior_tag=_FIERCE_STABBING_TAG),
        TalentComponent(name="Charger (DP on kill)", behavior_tag=_CHARGER_DP_TAG),
    ]
    return op
