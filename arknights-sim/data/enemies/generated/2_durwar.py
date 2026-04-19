"""湖畔救生员 — generated from ArknightsGameData enemy_1259_durwar_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1259_durwar_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_durwar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='湖畔救生员',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=420,
        defence=250,
        res=50.0,
        atk_interval=0.4,
        move_speed=0.95,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
