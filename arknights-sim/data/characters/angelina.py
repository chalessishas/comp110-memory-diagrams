"""Angelina — 6* Supporter (Decel Binder archetype).

Base stats from ArknightsGameData (E2 max, trust 100).
Talent 1 "Thoughtful": basic attack inflicts Slow(30%) for 0.8s (E2 rank).
S3 All for One: team ATK/ASPD buff aura — not yet wired.
"""
from __future__ import annotations
from core.state.unit_state import UnitState, RangeShape, TalentComponent, StatusEffect
from core.types import (
    AttackType, Faction, Profession, RoleArchetype, StatusKind,
)
from core.systems.talent_registry import register_talent
from data.characters.generated.angelina import make_angelina as _base_stats


# Decel Supporter standard range: wide cross (4 tiles forward + laterals)
DECEL_RANGE = RangeShape(tiles=(
    (1, 0), (2, 0), (3, 0), (4, 0),
    (1, 1), (2, 1), (1, -1), (2, -1),
))

_SLOW_TAG = "angelina_thoughtful_slow"
_SLOW_DURATION = 0.8    # seconds at E2 rank
_SLOW_AMOUNT = 0.30     # 30% movement reduction


def _on_attack_hit(world, attacker: UnitState, target: UnitState, damage: int) -> None:
    target.statuses.append(StatusEffect(
        kind=StatusKind.SLOW,
        source_tag=_SLOW_TAG,
        expires_at=world.global_state.elapsed + _SLOW_DURATION,
        params={"amount": _SLOW_AMOUNT},
    ))


register_talent(_SLOW_TAG, on_attack_hit=_on_attack_hit)


def make_angelina() -> UnitState:
    """Angelina E2 max, trust 100. Base stats from akgd; Thoughtful slow talent wired."""
    op = _base_stats()
    op.name = "Angelina"
    op.archetype = RoleArchetype.SUP_DECEL
    op.range_shape = DECEL_RANGE
    op.cost = 27
    op.talents = [TalentComponent(name="Thoughtful", behavior_tag=_SLOW_TAG)]
    return op
