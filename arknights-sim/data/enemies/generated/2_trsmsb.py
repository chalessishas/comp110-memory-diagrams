"""染污勇士 — generated from ArknightsGameData enemy_10005_trsmsb_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10005_trsmsb_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_trsmsb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='染污勇士',
        faction=Faction.ENEMY,
        max_hp=4800,
        atk=420,
        defence=350,
        res=0.0,
        atk_interval=1.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
