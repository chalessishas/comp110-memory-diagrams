"""寻路者狙击手 — generated from ArknightsGameData enemy_1213_mtrsnp level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1213_mtrsnp
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mtrsnp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='寻路者狙击手',
        faction=Faction.ENEMY,
        max_hp=3800,
        atk=300,
        defence=50,
        res=0.0,
        atk_interval=3.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
