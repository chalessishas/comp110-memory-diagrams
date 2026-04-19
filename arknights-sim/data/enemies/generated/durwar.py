"""湖畔志愿者 — generated from ArknightsGameData enemy_1259_durwar level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1259_durwar
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_durwar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='湖畔志愿者',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=320,
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
