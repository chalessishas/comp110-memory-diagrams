"""深池侦察犬 — generated from ArknightsGameData enemy_1165_duhond level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1165_duhond
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_duhond(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='深池侦察犬',
        faction=Faction.ENEMY,
        max_hp=2800,
        atk=300,
        defence=0,
        res=0.0,
        atk_interval=1.4,
        move_speed=1.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
