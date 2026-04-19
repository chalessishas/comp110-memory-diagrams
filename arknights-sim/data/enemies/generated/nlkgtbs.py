"""“暴食之果” — generated from ArknightsGameData enemy_6009_nlkgtbs level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6009_nlkgtbs
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_nlkgtbs(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“暴食之果”',
        faction=Faction.ENEMY,
        max_hp=55000,
        atk=1050,
        defence=1050,
        res=60.0,
        atk_interval=3.7,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
