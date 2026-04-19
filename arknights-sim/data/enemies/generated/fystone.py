"""粗圆岩 — generated from ArknightsGameData enemy_6006_fystone level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_6006_fystone
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_fystone(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='粗圆岩',
        faction=Faction.ENEMY,
        max_hp=2000,
        atk=0,
        defence=1000,
        res=50.0,
        atk_interval=1.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
