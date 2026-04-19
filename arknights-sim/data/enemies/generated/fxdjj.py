"""“绝对安保”试做型 — generated from ArknightsGameData enemy_6032_fxdjj level 0.
motion=WALK  applyWay=RANGED  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_6032_fxdjj
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_fxdjj(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“绝对安保”试做型',
        faction=Faction.ENEMY,
        max_hp=70000,
        atk=600,
        defence=800,
        res=40.0,
        atk_interval=2.5,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
