"""赫尔昏佐伦，“巫王” — generated from ArknightsGameData enemy_1548_ltniak level 0.
motion=WALK  applyWay=RANGED  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1548_ltniak
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ltniak(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='赫尔昏佐伦，“巫王”',
        faction=Faction.ENEMY,
        max_hp=80000,
        atk=750,
        defence=600,
        res=80.0,
        atk_interval=4.0,
        move_speed=1.0,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
