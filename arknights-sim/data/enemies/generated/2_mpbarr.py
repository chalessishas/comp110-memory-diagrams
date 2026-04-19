"""自助出餐终端原型机 — generated from ArknightsGameData enemy_10077_mpbarr_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10077_mpbarr_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mpbarr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='自助出餐终端原型机',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=900,
        defence=1300,
        res=50.0,
        atk_interval=2.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
