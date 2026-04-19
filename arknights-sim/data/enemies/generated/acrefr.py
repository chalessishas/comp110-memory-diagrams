"""假想敌：镜膜 — generated from ArknightsGameData enemy_9011_acrefr level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9011_acrefr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acrefr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='假想敌：镜膜',
        faction=Faction.ENEMY,
        max_hp=18000,
        atk=1000,
        defence=600,
        res=0.0,
        atk_interval=5.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
