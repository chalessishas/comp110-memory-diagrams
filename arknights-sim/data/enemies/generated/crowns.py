"""弑君者 — generated from ArknightsGameData enemy_1502_crowns level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1502_crowns
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_crowns(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='弑君者',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=400,
        defence=120,
        res=50.0,
        atk_interval=2.8,
        move_speed=1.4,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
