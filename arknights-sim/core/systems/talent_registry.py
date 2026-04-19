"""Talent registry — passive behavior hooks keyed by behavior_tag.

Talent callbacks:
  on_hit_received(world, defender, attacker, damage) → None
    Called after damage is dealt to defender by attacker (e.g. Liskarm arc).

  on_attack_hit(world, attacker, target, damage) → None
    Called after attacker deals damage to target (e.g. Angelina slow).

  on_kill(world, killer, killed) → None
    Called when killer lands the killing blow (e.g. Charger class DP on kill).

  on_battle_start(world, unit) → None
    Called once when a unit is added to the world (e.g. Texas Tactical Delivery +2 DP).

  on_tick(world, unit, dt) → None
    Called every tick for each deployed alive ally (e.g. Nearl passive HoT).

Usage:
    register_talent("texas_tactical_delivery", on_battle_start=_dp_cb)
"""
from __future__ import annotations
from typing import Callable, Dict, Optional, Tuple

_Fn = Callable  # type alias shorthand

_REGISTRY: Dict[str, Tuple] = {}
# value: (on_hit_received, on_attack_hit, on_kill, on_battle_start, on_tick)


def register_talent(
    tag: str,
    *,
    on_hit_received: Optional[_Fn] = None,
    on_attack_hit: Optional[_Fn] = None,
    on_kill: Optional[_Fn] = None,
    on_battle_start: Optional[_Fn] = None,
    on_tick: Optional[_Fn] = None,
) -> None:
    _REGISTRY[tag] = (on_hit_received, on_attack_hit, on_kill, on_battle_start, on_tick)


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


def fire_on_battle_start(world, unit) -> None:
    for talent in unit.talents:
        entry = _REGISTRY.get(talent.behavior_tag)
        if entry and len(entry) > 3 and entry[3]:
            entry[3](world, unit)


def fire_on_tick(world, unit, dt: float) -> None:
    for talent in unit.talents:
        entry = _REGISTRY.get(talent.behavior_tag)
        if entry and len(entry) > 4 and entry[4]:
            entry[4](world, unit, dt)
