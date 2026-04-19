"""“护目镜”帮派打手 — generated from ArknightsGameData enemy_10023_vtsnky_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10023_vtsnky_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_vtsnky(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“护目镜”帮派打手',
        faction=Faction.ENEMY,
        max_hp=4800,
        atk=410,
        defence=220,
        res=15.0,
        atk_interval=2.6,
        move_speed=0.85,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
