"""“漫游小屋” — generated from ArknightsGameData enemy_6007_mtslm level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6007_mtslm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mtslm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“漫游小屋”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=1000,
        defence=1500,
        res=40.0,
        atk_interval=2.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
