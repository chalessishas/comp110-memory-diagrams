"""“锅盖头”射手 — generated from ArknightsGameData enemy_1411_mmrnge level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1411_mmrnge
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mmrnge(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“锅盖头”射手',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=350,
        defence=200,
        res=60.0,
        atk_interval=3.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
