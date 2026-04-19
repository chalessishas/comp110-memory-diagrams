"""果冻小子 — generated from ArknightsGameData enemy_5503_arcslma level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5503_arcslma
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_arcslma(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='果冻小子',
        faction=Faction.ENEMY,
        max_hp=18000,
        atk=1100,
        defence=0,
        res=0.0,
        atk_interval=4.0,
        move_speed=0.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
