"""冰原战士队长 — generated from ArknightsGameData enemy_1189_krgaxe_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1189_krgaxe_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_krgaxe(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='冰原战士队长',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=350,
        defence=150,
        res=20.0,
        atk_interval=2.2,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
