"""荒原潜伏者 — generated from ArknightsGameData enemy_1338_bhrjst level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1338_bhrjst
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_bhrjst(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='荒原潜伏者',
        faction=Faction.ENEMY,
        max_hp=5300,
        atk=500,
        defence=330,
        res=0.0,
        atk_interval=2.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
