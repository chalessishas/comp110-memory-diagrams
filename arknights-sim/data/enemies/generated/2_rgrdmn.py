"""萨卡兹宿主卫巢百夫长 — generated from ArknightsGameData enemy_1114_rgrdmn_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1114_rgrdmn_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_rgrdmn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='萨卡兹宿主卫巢百夫长',
        faction=Faction.ENEMY,
        max_hp=14000,
        atk=700,
        defence=220,
        res=60.0,
        atk_interval=5.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
