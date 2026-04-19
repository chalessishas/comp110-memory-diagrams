"""血骑士狄开俄波利斯 — generated from ArknightsGameData enemy_1524_bldkgt level 0.
motion=WALK  applyWay=ALL  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1524_bldkgt
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_bldkgt(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='血骑士狄开俄波利斯',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=1750,
        defence=1000,
        res=40.0,
        atk_interval=6.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
