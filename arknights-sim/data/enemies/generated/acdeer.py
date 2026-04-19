"""“萨米的意志” — generated from ArknightsGameData enemy_9033_acdeer level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_9033_acdeer
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acdeer(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“萨米的意志”',
        faction=Faction.ENEMY,
        max_hp=240000,
        atk=800,
        defence=800,
        res=40.0,
        atk_interval=6.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
