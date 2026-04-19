"""Vigna — 4* Vanguard (Charger archetype).

Charger class trait: gains 1 DP when this unit kills an enemy.
Talent "Fierce Stabbing": 10% crit (×1.5 dmg), 30% during skill — NOT YET MODELED
(crit requires RNG in combat_system; deferred to avoid non-determinism in tests).
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent
from core.types import AttackType, Faction, Profession, RoleArchetype
from data.characters.generated.vigna import make_vigna as _base_stats
# Import from fang to ensure the Charger on_kill handler is registered
from data.characters.fang import _CHARGER_DP_TAG  # noqa: F401 (side-effect import)


CHARGER_RANGE = RangeShape(tiles=((0, 0), (1, 0)))


def make_vigna() -> UnitState:
    """Vigna E2 max. Charger class trait: +1 DP on kill."""
    op = _base_stats()
    op.name = "Vigna"
    op.archetype = RoleArchetype.VAN_CHARGER
    op.range_shape = CHARGER_RANGE
    op.block = 1
    op.cost = 11
    op.talents = [TalentComponent(
        name="Charger (DP on kill)",
        behavior_tag=_CHARGER_DP_TAG,
    )]
    return op
