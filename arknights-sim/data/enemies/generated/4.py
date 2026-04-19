"""退行的奠基者 — generated from ArknightsGameData enemy_1230_dsbudr_4 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1230_dsbudr_4
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_4(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='退行的奠基者',
        faction=Faction.ENEMY,
        max_hp=7000,
        atk=450,
        defence=200,
        res=30.0,
        atk_interval=3.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
