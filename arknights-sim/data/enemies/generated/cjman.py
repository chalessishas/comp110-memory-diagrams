"""丑言 — generated from ArknightsGameData enemy_10053_cjman level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10053_cjman
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cjman(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='丑言',
        faction=Faction.ENEMY,
        max_hp=4300,
        atk=330,
        defence=150,
        res=0.0,
        atk_interval=2.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
