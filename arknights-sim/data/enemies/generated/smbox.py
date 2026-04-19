"""巨壳藤蔓 — generated from ArknightsGameData enemy_2059_smbox level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_2059_smbox
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_smbox(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='巨壳藤蔓',
        faction=Faction.ENEMY,
        max_hp=10000,
        atk=600,
        defence=500,
        res=30.0,
        atk_interval=1.2,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
