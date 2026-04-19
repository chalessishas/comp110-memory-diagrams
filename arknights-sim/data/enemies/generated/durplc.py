"""钢铁冲浪教练 — generated from ArknightsGameData enemy_1262_durplc level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1262_durplc
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_durplc(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='钢铁冲浪教练',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=400,
        defence=800,
        res=10.0,
        atk_interval=3.0,
        move_speed=0.75,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
