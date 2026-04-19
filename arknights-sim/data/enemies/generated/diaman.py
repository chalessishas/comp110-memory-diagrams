"""磐蟹 — generated from ArknightsGameData enemy_1016_diaman level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1016_diaman
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_diaman(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='磐蟹',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=300,
        defence=500,
        res=85.0,
        atk_interval=2.3,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
