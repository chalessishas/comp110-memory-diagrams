"""Talent registry — passive behavior hooks keyed by behavior_tag.

Talent callbacks:
  on_hit_received(world, defender, attacker, damage) → None
    Called after damage is dealt to defender by attacker.

Usage:
    from core.systems.talent_registry import register_talent, fire_on_hit_received
    register_talent("liskarm_lightning", on_hit_received=_arc_callback)
"""
from __future__ import annotations
from typing import Callable, Dict, Optional, Tuple

_HitReceivedFn = Callable[["World", "UnitState", "UnitState", int], None]  # type: ignore[name-defined]

_REGISTRY: Dict[str, Tuple[Optional[_HitReceivedFn]]] = {}


def register_talent(
    tag: str,
    *,
    on_hit_received: Optional[_HitReceivedFn] = None,
) -> None:
    _REGISTRY[tag] = (on_hit_received,)


def fire_on_hit_received(world, defender, attacker, damage: int) -> None:
    for talent in defender.talents:
        entry = _REGISTRY.get(talent.behavior_tag)
        if entry and entry[0]:
            entry[0](world, defender, attacker, damage)
