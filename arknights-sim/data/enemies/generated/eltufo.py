"""“迷迭香”的无人机 — generated from ArknightsGameData enemy_8009_eltufo level 0.
motion=FLY  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_8009_eltufo
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_eltufo(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“迷迭香”的无人机',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=700,
        defence=550,
        res=40.0,
        atk_interval=5.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.AIRBORNE,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
