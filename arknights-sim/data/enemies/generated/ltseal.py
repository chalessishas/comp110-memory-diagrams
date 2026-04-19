"""血红阵地 — generated from ArknightsGameData enemy_1245_ltseal level 0.
motion=WALK  applyWay=NONE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1245_ltseal
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ltseal(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='血红阵地',
        faction=Faction.ENEMY,
        max_hp=5,
        atk=150,
        defence=0,
        res=0.0,
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
