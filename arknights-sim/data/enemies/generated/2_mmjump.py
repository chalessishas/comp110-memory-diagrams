"""破烂发明家 — generated from ArknightsGameData enemy_1412_mmjump_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1412_mmjump_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_mmjump(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='破烂发明家',
        faction=Faction.ENEMY,
        max_hp=7200,
        atk=660,
        defence=1400,
        res=60.0,
        atk_interval=1.2,
        move_speed=1.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
