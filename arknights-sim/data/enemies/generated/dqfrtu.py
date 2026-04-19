"""畸变之矛 — generated from ArknightsGameData enemy_15029_dqfrtu level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_15029_dqfrtu
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_dqfrtu(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='畸变之矛',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=1000,
        defence=2000,
        res=80.0,
        atk_interval=4.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
