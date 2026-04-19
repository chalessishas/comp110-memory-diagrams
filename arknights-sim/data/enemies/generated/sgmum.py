"""“以板之名” — generated from ArknightsGameData enemy_10019_sgmum level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10019_sgmum
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgmum(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“以板之名”',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=1500,
        defence=50,
        res=5.0,
        atk_interval=6.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
