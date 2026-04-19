"""“剧团喉舌” — generated from ArknightsGameData enemy_2019_cshost level 0.
motion=WALK  applyWay=RANGED  lifeReduce=30
Regenerate: python tools/gen_enemies.py enemy_2019_cshost
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cshost(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“剧团喉舌”',
        faction=Faction.ENEMY,
        max_hp=100000,
        atk=1000,
        defence=0,
        res=0.0,
        atk_interval=4.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
