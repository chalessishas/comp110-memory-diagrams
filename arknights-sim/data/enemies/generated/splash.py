"""干渴者 — generated from ArknightsGameData enemy_6016_splash level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_6016_splash
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_splash(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='干渴者',
        faction=Faction.ENEMY,
        max_hp=85000,
        atk=500,
        defence=1950,
        res=95.0,
        atk_interval=2.7,
        move_speed=0.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
