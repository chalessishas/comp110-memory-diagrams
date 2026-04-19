"""“美食速递” — generated from ArknightsGameData enemy_10038_cnvpiz_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10038_cnvpiz_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_cnvpiz(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“美食速递”',
        faction=Faction.ENEMY,
        max_hp=17000,
        atk=750,
        defence=800,
        res=20.0,
        atk_interval=5.0,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
