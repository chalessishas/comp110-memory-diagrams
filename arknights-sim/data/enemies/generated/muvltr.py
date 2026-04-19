"""赛场补给车 — generated from ArknightsGameData enemy_4004_muvltr level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_4004_muvltr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_muvltr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='赛场补给车',
        faction=Faction.ENEMY,
        max_hp=25000,
        atk=800,
        defence=600,
        res=50.0,
        atk_interval=1.0,
        move_speed=2.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
