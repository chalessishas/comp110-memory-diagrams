"""万国信使，奥伦 — generated from ArknightsGameData enemy_1219_mtrbty_2 level 0.
motion=WALK  applyWay=ALL  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1219_mtrbty_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mtrbty(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='万国信使，奥伦',
        faction=Faction.ENEMY,
        max_hp=23000,
        atk=700,
        defence=550,
        res=60.0,
        atk_interval=2.7,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
