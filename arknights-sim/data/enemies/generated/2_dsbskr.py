"""富营养的裂礁者 — generated from ArknightsGameData enemy_1235_dsbskr_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1235_dsbskr_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dsbskr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='富营养的裂礁者',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=400,
        defence=750,
        res=40.0,
        atk_interval=1.5,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
