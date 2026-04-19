"""匪帮斧手 — generated from ArknightsGameData enemy_1357_erob level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1357_erob
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_erob(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='匪帮斧手',
        faction=Faction.ENEMY,
        max_hp=16000,
        atk=500,
        defence=250,
        res=20.0,
        atk_interval=2.8,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
