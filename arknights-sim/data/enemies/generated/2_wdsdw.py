"""萨卡兹悖谬裂变术师 — generated from ArknightsGameData enemy_1324_wdsdw_2 level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1324_wdsdw_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_wdsdw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='萨卡兹悖谬裂变术师',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=500,
        defence=250,
        res=60.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
