"""Originium Drone (源石无人机) — aerial enemy, bypasses melee block."""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_drone(path: List[Tuple[int, int]] | None = None) -> UnitState:
    """Lv 0 Originium Drone. Mobility.AIRBORNE → not blocked by melee operators."""
    e = UnitState(
        name="Originium Drone",
        faction=Faction.ENEMY,
        max_hp=800,
        atk=150,
        defence=0,
        res=0.0,
        atk_interval=2.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        block=0,
        move_speed=1.5,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
