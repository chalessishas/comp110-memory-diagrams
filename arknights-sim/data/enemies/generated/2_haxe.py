"""高级武装人员 — generated from ArknightsGameData enemy_1035_haxe_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1035_haxe_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_haxe(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='高级武装人员',
        faction=Faction.ENEMY,
        max_hp=18000,
        atk=1500,
        defence=800,
        res=30.0,
        atk_interval=3.5,
        move_speed=0.65,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
