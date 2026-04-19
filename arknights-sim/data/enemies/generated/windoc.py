"""哈洛德·克雷加文 — generated from ArknightsGameData enemy_1549_windoc level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1549_windoc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_windoc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='哈洛德·克雷加文',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=800,
        defence=500,
        res=50.0,
        atk_interval=6.0,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
