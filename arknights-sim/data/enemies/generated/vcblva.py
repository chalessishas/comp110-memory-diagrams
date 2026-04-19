"""抗拒之火炎熔 — generated from ArknightsGameData enemy_8017_vcblva level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_8017_vcblva
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_vcblva(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='抗拒之火炎熔',
        faction=Faction.ENEMY,
        max_hp=70000,
        atk=700,
        defence=800,
        res=60.0,
        atk_interval=2.5,
        move_speed=1.2,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
