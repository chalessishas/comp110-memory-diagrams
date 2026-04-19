"""“街头醉汉” — generated from ArknightsGameData enemy_1238_ltmob_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1238_ltmob_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_ltmob(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='“街头醉汉”',
        faction=Faction.ENEMY,
        max_hp=4500,
        atk=520,
        defence=50,
        res=0.0,
        atk_interval=2.2,
        move_speed=1.3,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
