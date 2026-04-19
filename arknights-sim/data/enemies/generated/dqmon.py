"""普通的萨卡兹 — generated from ArknightsGameData enemy_5032_dqmon level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5032_dqmon
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqmon(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='普通的萨卡兹',
        faction=Faction.ENEMY,
        max_hp=7500,
        atk=600,
        defence=230,
        res=50.0,
        atk_interval=2.0,
        move_speed=0.85,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
