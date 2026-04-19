"""烛骑士薇薇安娜 — generated from ArknightsGameData enemy_1184_cadkgt_3 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1184_cadkgt_3
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_3_cadkgt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='烛骑士薇薇安娜',
        faction=Faction.ENEMY,
        max_hp=8500,
        atk=450,
        defence=350,
        res=60.0,
        atk_interval=3.2,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
