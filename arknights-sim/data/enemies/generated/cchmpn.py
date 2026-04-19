"""提亚卡乌勇士 — generated from ArknightsGameData enemy_1098_cchmpn level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_1098_cchmpn
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_cchmpn(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='提亚卡乌勇士',
        faction=Faction.ENEMY,
        max_hp=12000,
        atk=700,
        defence=950,
        res=10.0,
        atk_interval=4.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
