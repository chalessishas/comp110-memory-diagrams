"""岗哨密探 — generated from ArknightsGameData enemy_1315_wdyjd level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1315_wdyjd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_wdyjd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='岗哨密探',
        faction=Faction.ENEMY,
        max_hp=5500,
        atk=700,
        defence=150,
        res=35.0,
        atk_interval=3.3,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
