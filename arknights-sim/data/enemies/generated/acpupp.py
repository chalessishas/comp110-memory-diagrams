"""假想敌：再生 — generated from ArknightsGameData enemy_9010_acpupp level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9010_acpupp
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_acpupp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='假想敌：再生',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=1100,
        defence=300,
        res=40.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
