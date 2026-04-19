"""变格博士 — generated from ArknightsGameData enemy_5076_izdoc level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5076_izdoc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_izdoc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='变格博士',
        faction=Faction.ENEMY,
        max_hp=16000,
        atk=700,
        defence=0,
        res=0.0,
        atk_interval=1.6,
        move_speed=1.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
