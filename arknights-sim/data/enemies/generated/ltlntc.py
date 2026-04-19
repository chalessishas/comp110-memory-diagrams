"""冬灵血巫 — generated from ArknightsGameData enemy_1089_ltlntc level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1089_ltlntc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ltlntc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='冬灵血巫',
        faction=Faction.ENEMY,
        max_hp=20000,
        atk=500,
        defence=300,
        res=50.0,
        atk_interval=1.3,
        move_speed=1.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
