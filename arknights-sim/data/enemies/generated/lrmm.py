"""活性源石风暴 — generated from ArknightsGameData enemy_1420_lrmm level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1420_lrmm
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lrmm(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='活性源石风暴',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=900,
        defence=300,
        res=20.0,
        atk_interval=3.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
