"""心烛 — generated from ArknightsGameData enemy_5601_entlec level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5601_entlec
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_entlec(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='心烛',
        faction=Faction.ENEMY,
        max_hp=1000,
        atk=1000,
        defence=1000,
        res=1000.0,
        atk_interval=3.0,
        move_speed=0.45,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
