"""Talent registry — passive behavior hooks keyed by behavior_tag.

Talent callbacks:
  on_hit_received(world, defender, attacker, damage) → None
    Called after damage is dealt to defender by attacker (e.g. Liskarm arc).

  on_attack_hit(world, attacker, target, damage) → None
    Called after attacker deals damage to target (e.g. Angelina slow).

Usage:
    register_talent("liskarm_lightning", on_hit_received=_arc_cb)
    register_talent("angelina_slow", on_attack_hit=_slow_cb)
"""
from __future__ import annotations
from typing import Callable, Dict, Optional, Tuple

_Fn = Callable  # type alias shorthand

_REGISTRY: Dict[str, Tuple[Optional[_Fn], Optional[_Fn]]] = {}
# value: (on_hit_received, on_attack_hit)


def register_talent(
    tag: str,
    *,
    on_hit_received: Optional[_Fn] = None,
    on_attack_hit: Optional[_Fn] = None,
) -> None:
    _REGISTRY[tag] = (on_hit_received, on_attack_hit)


def fire_on_hit_received(world, defender, attacker, damage: int) -> None:
    for talent in defender.talents:
        entry = _REGISTRY.get(talent.behavior_tag)
        if entry and entry[0]:
            entry[0](world, defender, attacker, damage)


def fire_on_attack_hit(world, attacker, target, damage: int) -> None:
    for talent in attacker.talents:
        entry = _REGISTRY.get(talent.behavior_tag)
        if entry and entry[1]:
            entry[1](world, attacker, target, damage)
