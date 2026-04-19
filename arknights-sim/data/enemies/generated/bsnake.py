"""“不死的黑蛇” — generated from ArknightsGameData enemy_1515_bsnake level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1515_bsnake
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_bsnake(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“不死的黑蛇”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=770,
        defence=800,
        res=50.0,
        atk_interval=4.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
