"""引浪兽 — generated from ArknightsGameData enemy_4049_muston level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4049_muston
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_muston(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='引浪兽',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=600,
        defence=500,
        res=55.0,
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
