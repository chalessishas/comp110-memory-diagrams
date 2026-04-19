"""巴普洛维奇，枢密官 — generated from ArknightsGameData enemy_1587_ubbplwq level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1587_ubbplwq
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ubbplwq(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='巴普洛维奇，枢密官',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=1200,
        defence=600,
        res=15.0,
        atk_interval=3.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
