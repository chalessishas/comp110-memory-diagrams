"""失业萨克斯手 — generated from ArknightsGameData enemy_15003_dqltsw level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15003_dqltsw
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqltsw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='失业萨克斯手',
        faction=Faction.ENEMY,
        max_hp=17500,
        atk=800,
        defence=650,
        res=20.0,
        atk_interval=4.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
