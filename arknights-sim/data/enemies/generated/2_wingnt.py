"""“榴弹炮” — generated from ArknightsGameData enemy_1388_wingnt_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1388_wingnt_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_wingnt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“榴弹炮”',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=950,
        defence=800,
        res=20.0,
        atk_interval=3.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
