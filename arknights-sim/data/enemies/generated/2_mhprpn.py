"""箭棘兽 — generated from ArknightsGameData enemy_1310_mhprpn_2 level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1310_mhprpn_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mhprpn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='箭棘兽',
        faction=Faction.ENEMY,
        max_hp=35000,
        atk=720,
        defence=150,
        res=8.0,
        atk_interval=3.5,
        move_speed=0.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
