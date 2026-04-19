"""凶秽魔像 — generated from ArknightsGameData enemy_10006_trsmgi_2 level 0.
motion=WALK  applyWay=MELEE  lifeReduce=1
Regenerate: python tools/gen_enemies.py enemy_10006_trsmgi_2
"""
from __future__ import annotations
from typing import List, Tuple
from core.state.unit_state import UnitState
from core.types import AttackType, Faction, Mobility


def make_2_trsmgi(path: List[Tuple[int, int]] | None = None) -> UnitState:
    e = UnitState(
        name='凶秽魔像',
        faction=Faction.ENEMY,
        max_hp=45000,
        atk=1500,
        defence=50,
        res=0.0,
        atk_interval=6.0,
        move_speed=0.7,
        attack_type=AttackType.PHYSICAL,
        mobility=Mobility.GROUND,
        path=list(path) if path else [],
        deployed=True,
    )
    if e.path:
        e.position = (float(e.path[0][0]), float(e.path[0][1]))
    return e
