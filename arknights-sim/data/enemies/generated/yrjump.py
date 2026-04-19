"""破烂拼凑者 — generated from ArknightsGameData enemy_5063_yrjump level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_5063_yrjump
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_yrjump(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='破烂拼凑者',
        faction=Faction.ENEMY,
        max_hp=6000,
        atk=600,
        defence=1200,
        res=60.0,
        atk_interval=1.2,
        move_speed=1.1,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
