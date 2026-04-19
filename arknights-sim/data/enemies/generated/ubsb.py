"""强光恐吓者 — generated from ArknightsGameData enemy_10195_ubsb level 0.
motion=WALK  applyWay=RANGED  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10195_ubsb
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_ubsb(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='强光恐吓者',
        faction=Faction.ENEMY,
        max_hp=8000,
        atk=250,
        defence=250,
        res=5.0,
        atk_interval=3.2,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
