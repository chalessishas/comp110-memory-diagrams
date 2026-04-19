"""“领袖” — generated from ArknightsGameData enemy_1536_ncrmcr level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1536_ncrmcr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ncrmcr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“领袖”',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=800,
        defence=750,
        res=60.0,
        atk_interval=4.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
