"""荒原劫掠者 — generated from ArknightsGameData enemy_1339_bhrgrd level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1339_bhrgrd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_bhrgrd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='荒原劫掠者',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=500,
        defence=800,
        res=0.0,
        atk_interval=4.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
