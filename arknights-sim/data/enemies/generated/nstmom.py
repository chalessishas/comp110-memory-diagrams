"""女妖河谷的拂哀菈 — generated from ArknightsGameData enemy_1579_nstmom level 0.
motion=FLY  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1579_nstmom
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nstmom(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='女妖河谷的拂哀菈',
        faction=Faction.ENEMY,
        max_hp=70000,
        atk=1200,
        defence=2000,
        res=50.0,
        atk_interval=6.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
