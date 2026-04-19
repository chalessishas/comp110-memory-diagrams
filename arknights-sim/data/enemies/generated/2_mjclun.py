"""梦游大总管 — generated from ArknightsGameData enemy_10108_mjclun_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10108_mjclun_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mjclun(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='梦游大总管',
        faction=Faction.ENEMY,
        max_hp=27500,
        atk=900,
        defence=800,
        res=20.0,
        atk_interval=5.5,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
