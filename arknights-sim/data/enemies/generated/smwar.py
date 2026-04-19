"""木裂战士 — generated from ArknightsGameData enemy_2046_smwar level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_2046_smwar
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smwar(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='木裂战士',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=700,
        defence=800,
        res=20.0,
        atk_interval=1.2,
        move_speed=2.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
