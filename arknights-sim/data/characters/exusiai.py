"""Exusiai — 6* Sniper (Marksman archetype).

SOURCE: PRTS wiki, E2 L90, 信赖 100, no potentials, no module.
VERIFY: replace with akgd values next iteration.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape
from core.types import (
    AttackType, Faction, Profession, RoleArchetype,
)


# Marksman sniper standard range: 3×3 centered forward (simplified)
MARKSMAN_RANGE = RangeShape(tiles=tuple(
    (dx, dy) for dx in range(-1, 3) for dy in range(-1, 2)
))


def make_exusiai() -> UnitState:
    return UnitState(
        name="Exusiai",
        faction=Faction.ALLY,
        max_hp=2348,
        atk=705,
        defence=124,
        res=0.0,
        atk_interval=1.0,  # base; S2 Only Orange reduces it
        profession=Profession.SNIPER,
        archetype=RoleArchetype.SNIPER_MARKSMAN,
        attack_type=AttackType.PHYSICAL,
        attack_range_melee=False,
        block=0,
        range_shape=MARKSMAN_RANGE,
        cost=16,
        redeploy_cd=70.0,
    )
