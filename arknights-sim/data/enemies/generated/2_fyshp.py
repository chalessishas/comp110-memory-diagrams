"""风情街“满天飞空员” — generated from ArknightsGameData enemy_1347_fyshp_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1347_fyshp_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_fyshp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='风情街“满天飞空员”',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=650,
        defence=100,
        res=25.0,
        atk_interval=3.5,
        move_speed=0.35,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
