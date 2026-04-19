"""泥岩 — generated from ArknightsGameData enemy_1511_mdrock level 0.
motion=WALK  applyWay=MELEE  lifeReduce=2
Regenerate: python tools/gen_enemies.py enemy_1511_mdrock
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_mdrock(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='泥岩',
        faction=Faction.ENEMY,
        max_hp=45000,
        atk=800,
        defence=1000,
        res=30.0,
        atk_interval=4.5,
        move_speed=0.6,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
