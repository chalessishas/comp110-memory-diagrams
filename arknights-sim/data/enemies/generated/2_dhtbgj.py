"""身上的天标二 — generated from ArknightsGameData enemy_1400_dhtbgj_2 level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1400_dhtbgj_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dhtbgj(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='身上的天标二',
        faction=Faction.ENEMY,
        max_hp=1,
        atk=300,
        defence=0,
        res=0.0,
        atk_interval=1.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
