"""技师囚犯 — generated from ArknightsGameData enemy_9004_anlock level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_9004_anlock
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_anlock(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='技师囚犯',
        faction=Faction.ENEMY,
        max_hp=40000,
        atk=550,
        defence=500,
        res=40.0,
        atk_interval=3.0,
        move_speed=0.9,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
