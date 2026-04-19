"""“徘徊者” — generated from ArknightsGameData enemy_18005_lhwand level 0.
motion=WALK  applyWay=MELEE  lifeReduce=3
Regenerate: python tools/gen_enemies.py enemy_18005_lhwand
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_lhwand(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“徘徊者”',
        faction=Faction.ENEMY,
        max_hp=70000,
        atk=750,
        defence=2000,
        res=80.0,
        atk_interval=3.4,
        move_speed=0.8,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
