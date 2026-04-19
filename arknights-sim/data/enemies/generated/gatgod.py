"""翠梦祭司 — generated from ArknightsGameData enemy_7022_gatgod level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_7022_gatgod
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_gatgod(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='翠梦祭司',
        faction=Faction.ENEMY,
        max_hp=400000,
        atk=1500,
        defence=1200,
        res=30.0,
        atk_interval=2.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
