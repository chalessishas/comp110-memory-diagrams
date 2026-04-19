"""酗酒滋事者 — generated from ArknightsGameData enemy_10197_ublyb level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10197_ublyb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ublyb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='酗酒滋事者',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=600,
        defence=150,
        res=20.0,
        atk_interval=2.3,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
