"""Talent registry — passive behavior hooks keyed by behavior_tag.

Talent callbacks:
  on_hit_received(world, defender, attacker, damage) → None
    Called after damage is dealt to defender by attacker (e.g. Liskarm arc).

  on_attack_hit(world, attacker, target, damage) → None
    Called after attacker deals damage to target (e.g. Angelina slow).

  on_kill(world, killer, killed) → None
    Called when killer lands the killing blow (e.g. Vanguard Pioneer DP on kill).

Usage:
    register_talent("texas_dp_on_kill", on_kill=_dp_cb)
"""
from __future__ import annotations
from typing import Callable, Dict, Optional, Tuple

_Fn = Callable  # type alias shorthand

_REGISTRY: Dict[str, Tuple[Optional[_Fn], Optional[_Fn], Optional[_Fn]]] = {}
# value: (on_hit_received, on_attack_hit, on_kill)


def register_talent(
    tag: str,
    *,
    on_hit_received: Optional[_Fn] = None,
    on_attack_hit: Optional[_Fn] = None,
    on_kill: Optional[_Fn] = None,
) -> None:
    _REGISTRY[tag] = (on_hit_received, on_attack_hit, on_kill)


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


def fire_on_kill(world, killer, killed) -> None:
    for talent in killer.talents:
        entry = _REGISTRY.get(talent.behavior_tag)
        if entry and entry[2]:
            entry[2](world, killer, killed)
