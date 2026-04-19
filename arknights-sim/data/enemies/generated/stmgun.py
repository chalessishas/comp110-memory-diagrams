"""伦蒂尼姆城防自行炮 — generated from ArknightsGameData enemy_1273_stmgun level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1273_stmgun
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_stmgun(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='伦蒂尼姆城防自行炮',
        faction=Faction.ENEMY,
        max_hp=15000,
        atk=600,
        defence=1500,
        res=10.0,
        atk_interval=6.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
