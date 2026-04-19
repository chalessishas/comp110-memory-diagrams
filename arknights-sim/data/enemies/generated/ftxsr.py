"""指路芽 — generated from ArknightsGameData enemy_10068_ftxsr level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10068_ftxsr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ftxsr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='指路芽',
        faction=Faction.ENEMY,
        max_hp=5500,
        atk=320,
        defence=200,
        res=60.0,
        atk_interval=3.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
