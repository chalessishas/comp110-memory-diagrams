"""爆裂源石虫 — generated from ArknightsGameData enemy_7018_scarab level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7018_scarab
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_scarab(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='爆裂源石虫',
        faction=Faction.ENEMY,
        max_hp=9800,
        atk=3250,
        defence=285,
        res=10.0,
        atk_interval=5.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
