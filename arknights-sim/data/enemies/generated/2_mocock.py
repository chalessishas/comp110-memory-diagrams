"""燃烧瓶投掷者 — generated from ArknightsGameData enemy_1028_mocock_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1028_mocock_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mocock(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='燃烧瓶投掷者',
        faction=Faction.ENEMY,
        max_hp=2000,
        atk=250,
        defence=85,
        res=0.0,
        atk_interval=2.2,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
