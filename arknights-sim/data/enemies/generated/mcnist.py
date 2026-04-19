"""“Mechanist”，机械之心 — generated from ArknightsGameData enemy_8010_mcnist level 0.
motion=WALK  applyWay=ALL  lifeReduce=5
Regenerate: python tools/gen_enemies.py enemy_8010_mcnist
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mcnist(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“Mechanist”，机械之心',
        faction=Faction.ENEMY,
        max_hp=60000,
        atk=800,
        defence=1500,
        res=40.0,
        atk_interval=3.0,
        move_speed=0.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
