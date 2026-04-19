"""除秽 — generated from ArknightsGameData enemy_1390_dhsbr_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1390_dhsbr_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_dhsbr(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='除秽',
        faction=Faction.ENEMY,
        max_hp=3700,
        atk=330,
        defence=150,
        res=10.0,
        atk_interval=2.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
