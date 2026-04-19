"""重装防御者 — generated from ArknightsGameData enemy_1006_shield level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1006_shield
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_shield(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='重装防御者',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=600,
        defence=800,
        res=0.0,
        atk_interval=2.6,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
