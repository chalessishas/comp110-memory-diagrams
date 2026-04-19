"""暗潮钳兽·α — generated from ArknightsGameData enemy_1178_dscorp_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1178_dscorp_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dscorp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='暗潮钳兽·α',
        faction=Faction.ENEMY,
        max_hp=2800,
        atk=400,
        defence=400,
        res=30.0,
        atk_interval=2.1,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
