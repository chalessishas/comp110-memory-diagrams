"""“私人安全顾问” — generated from ArknightsGameData enemy_1588_ubbphw level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1588_ubbphw
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ubbphw(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“私人安全顾问”',
        faction=Faction.ENEMY,
        max_hp=50000,
        atk=700,
        defence=2000,
        res=50.0,
        atk_interval=3.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
