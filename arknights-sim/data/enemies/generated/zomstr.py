"""宿主拾荒者 — generated from ArknightsGameData enemy_1044_zomstr level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1044_zomstr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_zomstr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='宿主拾荒者',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=500,
        defence=130,
        res=30.0,
        atk_interval=3.0,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
