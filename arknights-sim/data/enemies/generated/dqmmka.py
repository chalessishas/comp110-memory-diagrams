"""安逸的驮兽 — generated from ArknightsGameData enemy_15014_dqmmka level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15014_dqmmka
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqmmka(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='安逸的驮兽',
        faction=Faction.ENEMY,
        max_hp=65000,
        atk=1800,
        defence=50,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
