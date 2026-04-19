"""水手长重艇 — generated from ArknightsGameData enemy_1163_hvymot_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1163_hvymot_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_hvymot(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='水手长重艇',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=1400,
        defence=1200,
        res=0.0,
        atk_interval=5.0,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
