"""米奥，热烈的考验者 — generated from ArknightsGameData enemy_10020_sgcat level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10020_sgcat
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_sgcat(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='米奥，热烈的考验者',
        faction=Faction.ENEMY,
        max_hp=30000,
        atk=800,
        defence=1000,
        res=50.0,
        atk_interval=5.0,
        move_speed=0.5,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
