"""岩壳蟹 — generated from ArknightsGameData enemy_7006_xbcrab level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7006_xbcrab
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_xbcrab(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='岩壳蟹',
        faction=Faction.ENEMY,
        max_hp=3000,
        atk=400,
        defence=800,
        res=70.0,
        atk_interval=2.5,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
