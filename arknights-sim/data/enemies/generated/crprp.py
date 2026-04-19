"""疲倦道具师 — generated from ArknightsGameData enemy_10096_crprp level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10096_crprp
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_crprp(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='疲倦道具师',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=200,
        defence=200,
        res=20.0,
        atk_interval=2.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
