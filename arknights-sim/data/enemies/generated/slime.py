"""源石虫 — generated from ArknightsGameData enemy_1007_slime level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1007_slime
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_slime(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='源石虫',
        faction=Faction.ENEMY,
        max_hp=550,
        atk=130,
        defence=0,
        res=0.0,
        atk_interval=1.7,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
