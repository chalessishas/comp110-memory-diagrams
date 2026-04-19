"""锏 — generated from ArknightsGameData enemy_1525_blkswb level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1525_blkswb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_blkswb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='锏',
        faction=Faction.ENEMY,
        max_hp=28000,
        atk=900,
        defence=600,
        res=50.0,
        atk_interval=4.0,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
