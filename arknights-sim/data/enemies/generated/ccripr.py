"""提亚卡乌好战者 — generated from ArknightsGameData enemy_1095_ccripr level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1095_ccripr
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ccripr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='提亚卡乌好战者',
        faction=Faction.ENEMY,
        max_hp=5500,
        atk=320,
        defence=380,
        res=10.0,
        atk_interval=1.0,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
