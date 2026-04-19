"""萨卡兹刀兵 — generated from ArknightsGameData enemy_1071_dftman level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1071_dftman
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dftman(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='萨卡兹刀兵',
        faction=Faction.ENEMY,
        max_hp=2800,
        atk=300,
        defence=70,
        res=50.0,
        atk_interval=2.5,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
