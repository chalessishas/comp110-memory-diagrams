"""狂躁异质裂兽 — generated from ArknightsGameData enemy_1571_mirbst level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1571_mirbst
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mirbst(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='狂躁异质裂兽',
        faction=Faction.ENEMY,
        max_hp=150000,
        atk=1000,
        defence=300,
        res=40.0,
        atk_interval=3.5,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
