"""大富翁 — generated from ArknightsGameData enemy_5501_arcbank level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5501_arcbank
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_arcbank(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='大富翁',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=1400,
        defence=1500,
        res=60.0,
        atk_interval=5.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
