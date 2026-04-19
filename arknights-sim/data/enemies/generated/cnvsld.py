"""业余竞演者 — generated from ArknightsGameData enemy_10031_cnvsld level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10031_cnvsld
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cnvsld(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='业余竞演者',
        faction=Faction.ENEMY,
        max_hp=4000,
        atk=300,
        defence=100,
        res=0.0,
        atk_interval=2.0,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
