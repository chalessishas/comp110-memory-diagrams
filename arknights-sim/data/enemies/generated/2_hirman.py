"""碎岩者组长 — generated from ArknightsGameData enemy_1048_hirman_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1048_hirman_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_hirman(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='碎岩者组长',
        faction=Faction.ENEMY,
        max_hp=13000,
        atk=900,
        defence=100,
        res=40.0,
        atk_interval=3.3,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
