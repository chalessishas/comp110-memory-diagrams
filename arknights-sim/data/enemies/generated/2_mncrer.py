"""见习祭司学徒 — generated from ArknightsGameData enemy_10156_mncrer_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10156_mncrer_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mncrer(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='见习祭司学徒',
        faction=Faction.ENEMY,
        max_hp=5500,
        atk=360,
        defence=100,
        res=20.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
