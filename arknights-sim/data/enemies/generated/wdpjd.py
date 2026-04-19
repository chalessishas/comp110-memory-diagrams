"""武装密探 — generated from ArknightsGameData enemy_1316_wdpjd level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1316_wdpjd
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_wdpjd(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='武装密探',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=1000,
        defence=1200,
        res=0.0,
        atk_interval=3.5,
        move_speed=0.35,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
